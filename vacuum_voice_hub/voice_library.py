"""Privacy-conscious local index of Creator voice packs with real audio hashes.

An author's metadata or declared license is not independent legal verification.
No prerecorded voices, user paths or author credentials leave local disk.
"""
import hashlib
import json
import re
from pathlib import Path

from .creator import MAX_AUDIO_BYTES, validate_workspace
from .translation_overlays import _no_duplicate_keys

SCHEMA = "vvh.local-voice-library.v1"
MAX_PACKS = 128
MAX_EVENTS = 256
MAX_ARCHIVE = 1024 * 1024
MAX_MANIFEST = 256 * 1024
MAX_PACK_AUDIO_BYTES = 256 * 1024 * 1024
SHA = re.compile(r"^[0-9a-f]{64}$")


def _hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _stable(doc):
    return json.dumps(doc, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _pack(path):
    origin = Path(path).expanduser().absolute()
    if origin.is_symlink() or not origin.is_dir():
        raise ValueError("Creator workspace must be a regular directory")
    root = origin.resolve(strict=True)
    manifest_path = root / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("Creator manifest must be a regular file")
    if manifest_path.stat().st_size > MAX_MANIFEST:
        raise ValueError("Creator manifest exceeds 256 KiB")
    original_digest = _hash(manifest_path)
    validation = validate_workspace(root)
    if not validation["ok"]:
        raise ValueError("invalid Creator voice pack: " + "; ".join(validation["errors"]))
    manifest = validation["manifest"]
    assignments = manifest["events"]
    if not 1 <= len(assignments) <= MAX_EVENTS:
        raise ValueError("library pack needs 1..256 audio assignments")
    rows, total = [], 0
    for semantic, relative in sorted(assignments.items()):
        source = root / relative
        if source.is_symlink() or any(parent.is_symlink() for parent in source.parents if parent != root):
            raise ValueError("voice library rejects symlinked clips")
        real = source.resolve(strict=True)
        real.relative_to(root)
        size = real.stat().st_size
        if not 0 < size <= MAX_AUDIO_BYTES:
            raise ValueError("invalid Creator audio length")
        total += size
        if total > MAX_PACK_AUDIO_BYTES:
            raise ValueError("library pack audio exceeds 256 MiB")
        rows.append({"semantic": semantic, "bytes": size, "sha256": _hash(real)})
    if _hash(manifest_path) != original_digest:
        raise ValueError("Creator manifest modified during indexing")
    fields = ("id", "name", "author", "license", "language")
    if any(not isinstance(manifest.get(k), str) or
           not 1 <= len(manifest[k].strip()) <= 128 for k in fields):
        raise ValueError("invalid Creator voice library metadata")
    return {
        "pack_id": manifest["id"], "title": manifest["name"],
        "author": manifest["author"], "license_declared": manifest["license"],
        "language": manifest["language"], "events": len(rows),
        "audio_bytes": total,
        "manifest_sha256": original_digest,
        "audio_fingerprint_sha256": hashlib.sha256(_stable(rows)).hexdigest(),
        "rights_independently_verified": False,
        "spoken_language_independently_verified": False,
        "hardware_install_verified": False,
    }


def _audit(record):
    if not isinstance(record, dict) or set(record) != {
        "schema", "packs", "index_sha256", "contains_audio",
        "rights_independently_verified", "install_authorized",
    } or record["schema"] != SCHEMA:
        raise ValueError("invalid voice library schema")
    if record["contains_audio"] is not False or record["rights_independently_verified"] is not False or record["install_authorized"] is not False:
        raise ValueError("library may not claim audio rights, install or embedded clips")
    digest = record.get("index_sha256")
    expected = hashlib.sha256(_stable({k:v for k,v in record.items() if k != "index_sha256"})).hexdigest()
    if not isinstance(digest, str) or digest != expected:
        raise ValueError("library index checksum mismatch")
    entries = record.get("packs")
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_PACKS:
        raise ValueError("library index pack count invalid")
    if entries != sorted(entries, key=lambda p: p["pack_id"]):
        raise ValueError("library pack sort order mismatch")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "pack_id", "title", "author", "license_declared", "language",
            "events", "audio_bytes", "manifest_sha256",
            "audio_fingerprint_sha256", "rights_independently_verified",
            "spoken_language_independently_verified", "hardware_install_verified"
        }:
            raise ValueError("invalid library pack entry")
        if entry["pack_id"] in seen:
            raise ValueError("duplicate voice library pack identity")
        seen.add(entry["pack_id"])
        for field in ("manifest_sha256","audio_fingerprint_sha256"):
            if not isinstance(entry[field], str) or not SHA.fullmatch(entry[field]):
                raise ValueError("invalid library source hash")
        if not all(entry[k] is False for k in (
                "rights_independently_verified","spoken_language_independently_verified",
                "hardware_install_verified")):
            raise ValueError("invalid voice library approval claim")
        if type(entry["events"]) is not int or not 1 <= entry["events"] <= MAX_EVENTS:
            raise ValueError("invalid library event count")
        if type(entry["audio_bytes"]) is not int or not 1 <= entry["audio_bytes"] <= MAX_PACK_AUDIO_BYTES:
            raise ValueError("invalid library audio length")
        for key in ("pack_id", "title", "author", "license_declared", "language"):
            val = entry[key]
            if not isinstance(val, str) or not 1 <= len(val.strip()) <= 128:
                raise ValueError("invalid library text metadata")
    return {"schema": SCHEMA, "pack_count": len(entries),
            "languages": sorted({e["language"] for e in entries}),
            "index_sha256": digest, "source_paths_included": False,
            "audio_bytes_included": False,
            "rights_independently_verified": False, "install_authorized": False}


def _load(path):
    source = Path(path).expanduser()
    if source.is_symlink() or not source.is_file():
        raise ValueError("library index must be a local regular file")
    with source.open("rb") as stream:
        data = stream.read(MAX_ARCHIVE + 1)
    if not 1 <= len(data) <= MAX_ARCHIVE:
        raise ValueError("library index exceeds 1 MiB")
    try:
        doc = json.loads(data.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid library index JSON") from exc
    _audit(doc)
    return doc


def create_library(workspaces, output):
    if isinstance(workspaces, str) or not isinstance(workspaces, (tuple, list)):
        raise ValueError("workspaces must be a list")
    if not 1 <= len(workspaces) <= MAX_PACKS:
        raise ValueError("library requires 1..128 workspaces")
    rows = sorted((_pack(p) for p in workspaces), key=lambda x: x["pack_id"])
    ids = [p["pack_id"] for p in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate Creator pack ids")
    doc = {"schema": SCHEMA, "packs": rows, "index_sha256": "",
           "contains_audio": False,
           "rights_independently_verified": False, "install_authorized": False}
    doc["index_sha256"] = hashlib.sha256(_stable({k:v for k,v in doc.items() if k != "index_sha256"})).hexdigest()
    payload = json.dumps(doc, indent=2, ensure_ascii=False,
                         sort_keys=True).encode("utf-8") + b"\n"
    if len(payload) > MAX_ARCHIVE:
        raise ValueError("voice library index exceeds 1 MiB")
    dest = Path(output).expanduser().absolute()
    if dest.suffix.lower() != ".json" or dest.exists() or dest.is_symlink():
        raise FileExistsError("library index output must be a new .json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("xb") as target:
        try:
            target.write(payload)
        except BaseException:
            target.close()
            dest.unlink(missing_ok=True)
            raise
    return {"output": str(dest), **_audit(doc)}


def audit_library(path):
    return _audit(_load(path))


def search_library(path, *, language=None, query=None, license_name=None):
    doc = _load(path)
    result = doc["packs"]
    if language:
        result = [r for r in result if r["language"].casefold() == language.casefold()]
    if license_name:
        result = [r for r in result if r["license_declared"].casefold() == license_name.casefold()]
    if query:
        needle = query.casefold()
        result = [r for r in result if needle in
                  (r["title"]+" "+r["author"]+" "+r["pack_id"]).casefold()]
    return {"schema": SCHEMA, "matching_packs": len(result), "packs": result,
            "license_is_self_declared_not_verified": True,
            "source_paths_included": False, "contains_audio": False,
            "install_authorized": False}


def reconcile_library(path, workspaces):
    doc = _load(path)
    if isinstance(workspaces, str) or not isinstance(workspaces, (tuple,list)) or not 1 <= len(workspaces) <= MAX_PACKS:
        raise ValueError("1..128 local source workspaces required")
    latest = sorted((_pack(p) for p in workspaces), key=lambda p:p["pack_id"])
    if len({p["pack_id"] for p in latest}) != len(latest):
        raise ValueError("duplicate Creator pack IDs")
    existing = {p["pack_id"]:p for p in doc["packs"]}
    current = {p["pack_id"]:p for p in latest}
    changed = sorted(k for k in existing.keys() & current.keys()
                     if existing[k] != current[k])
    return {"schema": SCHEMA, "matches": not changed and existing.keys() == current.keys(),
            "modified_packs": changed,
            "missing_packs": sorted(existing.keys() - current.keys()),
            "added_packs": sorted(current.keys() - existing.keys()),
            "rights_independently_verified": False,
            "install_authorized": False}
