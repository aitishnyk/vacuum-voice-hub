"""Extensible offline adapter interchange format; no executable plugin loading.

This produces a deterministic user-owned ZIP with raw Creator recordings and
verified semantic/event mapping, NOT any manufacturer-signed install package.
"""
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .catalog import event_by_semantic, event_profile_for_model, model_by_id
from .creator import MAX_AUDIO_BYTES, validate_workspace
from .translation_overlays import _no_duplicate_keys

SCHEMA = "vvh.adapter-descriptor.v1"
PACKAGE_SCHEMA = "vvh.adapter-interchange.v1"
MAX_DESCRIPTOR_BYTES = 64 * 1024
MAX_MANIFEST_BYTES = 256 * 1024
MAX_EVENTS = 128
MAX_PACKAGE_BYTES = 100 * 1024 * 1024
NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{2,60}$")
FILENAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}\.(?:wav|ogg|mp3|flac|aac|m4a|opus)$")
SHA = re.compile(r"^[a-f0-9]{64}$")
DT = (1980, 1, 1, 0, 0, 0)


def _json_file(path, max_bytes):
    source = Path(path).expanduser()
    if source.is_symlink() or not source.is_file():
        raise ValueError("source must be a regular local file")
    with source.open("rb") as stream:
        raw = stream.read(max_bytes + 1)
    if not 1 <= len(raw) <= max_bytes:
        raise ValueError("source JSON empty or exceeds bound")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_keys), hashlib.sha256(raw).hexdigest()
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid UTF-8 adapter JSON") from exc


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as inp:
        while chunk := inp.read(65536):
            digest.update(chunk)
    return digest.hexdigest()


def _check_descriptor(doc):
    if not isinstance(doc, dict) or set(doc) != {
        "schema", "adapter_id", "model_id", "author", "license", "entries"
    } or doc["schema"] != SCHEMA:
        raise ValueError("invalid adapter descriptor schema")
    if not isinstance(doc["adapter_id"], str) or not NAME.fullmatch(doc["adapter_id"]):
        raise ValueError("invalid adapter id")
    model = model_by_id(doc["model_id"])
    if model["id"] != doc["model_id"]:
        raise ValueError("exact canonical model required (aliases refused)")
    for key in ("author", "license"):
        value = doc[key]
        if not isinstance(value, str) or not 1 <= len(value.strip()) <= 128 or value != value.strip():
            raise ValueError("adapter " + key + " required")
    entries = doc["entries"]
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_EVENTS:
        raise ValueError("adapter descriptor needs 1..128 events")
    seen_semantics, seen_names, seen_ids = set(), set(), set()
    allowed = set(event_profile_for_model(model["id"])["known_event_ids"])
    mapped = []
    for item in entries:
        if not isinstance(item, dict) or set(item) != {"semantic", "archive_name"}:
            raise ValueError("adapter event entry fields invalid")
        semantic, name = item["semantic"], item["archive_name"]
        if not isinstance(semantic, str) or not isinstance(name, str) or not FILENAME.fullmatch(name):
            raise ValueError("invalid adapter semantic or archive filename")
        ids = sorted({int(e["id"]) for e in event_by_semantic(semantic) if int(e["id"]) in allowed})
        if not ids:
            raise ValueError("adapter semantic does not map to exact model")
        if semantic in seen_semantics or name.casefold() in seen_names or any(i in seen_ids for i in ids):
            raise ValueError("duplicate or ambiguous adapter semantic, archive filename or event ID")
        seen_semantics.add(semantic)
        seen_names.add(name.casefold())
        seen_ids.update(ids)
        mapped.append({"semantic": semantic, "archive_name": name, "target_event_ids": ids})
    return mapped


def _prepare(workspace, descriptor):
    doc, descriptor_sha = _json_file(descriptor, MAX_DESCRIPTOR_BYTES)
    mapped = _check_descriptor(doc)
    validation = validate_workspace(workspace)
    if not validation["ok"]:
        raise ValueError("invalid Creator workspace: " + "; ".join(validation["errors"]))
    root = Path(validation["workspace"]).resolve()
    manifest = validation["manifest"]
    results = []
    aggregate = 0
    for row in mapped:
        semantic = row["semantic"]
        rel = manifest["events"].get(semantic)
        if not isinstance(rel, str):
            raise ValueError("adapter semantic not assigned in Creator workspace")
        source = root / rel
        # Refuse symlinked recordings and intermediate symlink directories,
        # even when the resolved target remains inside the workspace.
        if source.is_symlink() or any(p.is_symlink() for p in source.parents if p != root):
            raise ValueError("symlinked adapter recordings are unsupported")
        actual = source.resolve(strict=True)
        actual.relative_to(root)
        if actual.suffix.lower() != Path(row["archive_name"]).suffix.lower():
            raise ValueError("archive extension cannot misrepresent source encoding")
        size = actual.stat().st_size
        if not 0 < size <= MAX_AUDIO_BYTES:
            raise ValueError("adapter clip missing or exceeds 25 MiB")
        aggregate += size
        if aggregate > MAX_PACKAGE_BYTES:
            raise ValueError("adapter interchange exceeds 100 MiB")
        results.append({**row, "bytes": size, "sha256": _sha(actual), "_path": actual})
    info = {
        "schema": PACKAGE_SCHEMA, "adapter_id": doc["adapter_id"],
        "model_id": doc["model_id"], "author": doc["author"],
        "license": doc["license"], "descriptor_sha256": descriptor_sha,
        "workspace_manifest_sha256": _sha(root / "manifest.json"),
        "entries": [{k: v for k, v in row.items() if k != "_path"} for row in results],
        "total_audio_bytes": aggregate,
        "third_party_code_executed": False, "official_vendor_package": False,
        "hardware_verified": False, "install_authorized": False,
        "redistribution_rights_verified": False,
    }
    return root, results, info


def adapter_preflight(workspace, descriptor):
    _, _, manifest = _prepare(workspace, descriptor)
    return {**manifest, "ready_for_offline_interchange": True,
            "source_paths_included": False}


def _zipentry(name, data, archive):
    info = zipfile.ZipInfo(name, date_time=DT)
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = (0o100644 << 16)
    archive.writestr(info, data)


def build_interchange(workspace, descriptor, output):
    root, files, metadata = _prepare(workspace, descriptor)
    dest = Path(output).expanduser().absolute()
    if dest.suffix.lower() != ".zip" or dest.is_symlink() or dest.exists():
        raise FileExistsError("adapter interchange output must be a new ZIP")
    if root == dest or root in dest.parents:
        raise ValueError("adapter package must be outside Creator workspace")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("xb") as out:
        try:
            with zipfile.ZipFile(out, "w") as archive:
                for row in sorted(files, key=lambda r: r["archive_name"]):
                    contents = row["_path"].read_bytes()
                    if len(contents) != row["bytes"] or hashlib.sha256(contents).hexdigest() != row["sha256"]:
                        raise ValueError("audio source changed during packaging")
                    _zipentry("audio/" + row["archive_name"], contents, archive)
                if _sha(root / "manifest.json") != metadata["workspace_manifest_sha256"]:
                    raise ValueError("Creator manifest changed during packaging")
                payload = json.dumps(metadata, ensure_ascii=False, indent=2,
                                     sort_keys=True).encode("utf-8") + b"\n"
                _zipentry("manifest.json", payload, archive)
        except BaseException:
            out.close()
            dest.unlink(missing_ok=True)
            raise
    try:
        verified = verify_interchange(dest)
    except BaseException:
        dest.unlink(missing_ok=True)
        raise
    return {"output": str(dest), "sha256": _sha(dest), "bytes": dest.stat().st_size,
            **verified}


def verify_interchange(path):
    source = Path(path).expanduser()
    if source.is_symlink() or not source.is_file():
        raise ValueError("adapter archive must be a regular file")
    if source.stat().st_size > MAX_PACKAGE_BYTES + MAX_MANIFEST_BYTES + 100000:
        raise ValueError("adapter archive oversized")
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        if not 2 <= len(infos) <= MAX_EVENTS + 1:
            raise ValueError("wrong adapter archive member count")
        names = [part.filename for part in infos]
        if len(names) != len(set(names)) or names[-1] != "manifest.json":
            raise ValueError("missing or duplicated adapter manifest")
        if any(p.compress_type != zipfile.ZIP_STORED or p.flag_bits & 1 for p in infos):
            raise ValueError("unsupported archive compression or encryption")
        if infos[-1].file_size > MAX_MANIFEST_BYTES:
            raise ValueError("adapter manifest oversized")
        try:
            doc = json.loads(archive.read(infos[-1]).decode("utf-8"),
                             object_pairs_hook=_no_duplicate_keys)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid adapter manifest") from exc
        if not isinstance(doc, dict) or doc.get("schema") != PACKAGE_SCHEMA:
            raise ValueError("incorrect interchange schema")
        if any(doc.get(k) is not False for k in (
                "official_vendor_package", "hardware_verified", "install_authorized",
                "redistribution_rights_verified", "third_party_code_executed")):
            raise ValueError("interchange must not claim rights or device support")
        rows = doc.get("entries")
        if not isinstance(rows, list) or len(rows) != len(infos) - 1:
            raise ValueError("adapter manifest entry count mismatch")
        if not NAME.fullmatch(str(doc.get("adapter_id", ""))) or not SHA.fullmatch(str(doc.get("descriptor_sha256", ""))):
            raise ValueError("invalid adapter manifest identity")
        model = model_by_id(doc.get("model_id"))
        if model["id"] != doc["model_id"]:
            raise ValueError("noncanonical adapter model")
        wanted = []
        total = 0
        for row in rows:
            if not isinstance(row, dict) or set(row) != {
                "semantic", "archive_name", "target_event_ids", "bytes", "sha256"
            }:
                raise ValueError("invalid interchange audio metadata")
            name = row["archive_name"]
            if not isinstance(name, str) or not FILENAME.fullmatch(name):
                raise ValueError("unsafe interchange member")
            if type(row["bytes"]) is not int or not 0 < row["bytes"] <= MAX_AUDIO_BYTES:
                raise ValueError("invalid interchange audio length")
            if not isinstance(row["sha256"], str) or not SHA.fullmatch(row["sha256"]):
                raise ValueError("invalid interchange audio checksum")
            total += row["bytes"]
            if total > MAX_PACKAGE_BYTES:
                raise ValueError("interchange exceeds 100 MiB")
            wanted.append("audio/" + name)
            source_info = archive.getinfo("audio/" + name) if "audio/" + name in names else None
            if source_info is None or source_info.file_size != row["bytes"]:
                raise ValueError("interchange entry length mismatch")
            digest = hashlib.sha256()
            with archive.open(source_info) as audio:
                while piece := audio.read(65536):
                    digest.update(piece)
            if digest.hexdigest() != row["sha256"]:
                raise ValueError("adapter audio checksum mismatch")
        if len(wanted) != len(set(wanted)) or sorted(names[:-1]) != sorted(wanted):
            raise ValueError("interchange contains unknown, duplicated or missing audio files")
        if doc.get("total_audio_bytes") != total:
            raise ValueError("interchange total bytes mismatch")
    return {"schema": PACKAGE_SCHEMA, "model_id": doc["model_id"],
            "adapter_id": doc["adapter_id"], "clip_count": len(rows),
            "total_audio_bytes": total, "integrity_verified": True,
            "manufacturer_format_verified": False,
            "hardware_verified": False, "install_authorized": False,
            "redistribution_rights_verified": False}
