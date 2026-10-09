"""Deterministic non-destructive local Creator project backups and recovery.

Contains only explicitly assigned project audio plus its manifest.
No cloud upload, robot connectivity, filesystem overwrite or rights proof.
"""
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

from .creator import MAX_AUDIO_BYTES, validate_workspace
from .translation_overlays import _no_duplicate_keys

SCHEMA = "vvh.creator-recovery.v1"
MAX_CLIPS = 256
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_MANIFEST_BYTES = 256 * 1024
SHA = re.compile(r"^[0-9a-f]{64}$")
AUDIO_PATH = re.compile(r"^audio/[a-zA-Z0-9][a-zA-Z0-9._-]{0,180}\.(?:wav|mp3|ogg|flac|m4a|aac|opus)$")
DATE = (1980, 1, 1, 0, 0, 0)


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _filehash(source):
    h = hashlib.sha256()
    with Path(source).open("rb") as stream:
        while chunk := stream.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _index(root):
    root = Path(root).expanduser().absolute()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Creator project must be a regular directory")
    root = root.resolve(strict=True)
    manifest_path = root / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("Creator manifest must be a regular file")
    if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError("Creator manifest exceeds 256 KiB")
    with manifest_path.open("rb") as inp:
        original = inp.read(MAX_MANIFEST_BYTES + 1)
    try:
        document = json.loads(original.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid Creator manifest JSON") from exc
    validation = validate_workspace(root)
    if not validation["ok"] or validation["manifest"] != document:
        raise ValueError("Creator workspace is invalid or changed during inspection")
    events = document["events"]
    paths = sorted(set(events.values()))
    if not 1 <= len(paths) <= MAX_CLIPS:
        raise ValueError("backup requires 1..256 assigned audio clips")
    rows, total = [], len(original)
    for rel in paths:
        if not isinstance(rel, str) or not AUDIO_PATH.fullmatch(rel):
            raise ValueError("backup supports flat local audio/ filenames only")
        candidate = root / rel
        if candidate.is_symlink() or any(p.is_symlink() for p in candidate.parents if p != root):
            raise ValueError("backup refuses symlinked audio")
        actual = candidate.resolve(strict=True)
        actual.relative_to(root)
        size = actual.stat().st_size
        if not 0 < size <= MAX_AUDIO_BYTES:
            raise ValueError("backup audio file missing or larger than 25 MiB")
        total += size
        if total > MAX_ARCHIVE_BYTES:
            raise ValueError("Creator backup exceeds 256 MiB")
        rows.append({"path": rel, "bytes": size, "sha256": _filehash(actual)})
    if _filehash(manifest_path) != _hash(original):
        raise ValueError("Creator manifest changed while preparing backup")
    return root, original, rows, {
        "schema": SCHEMA, "pack_id": document["id"],
        "manifest_sha256": _hash(original), "audio": rows,
        "audio_count": len(rows), "total_source_bytes": total,
        "source_rights_independently_verified": False,
        "independent_device_verified": False,
        "install_authorized": False,
    }


def _entry(archive, name, payload):
    zi = zipfile.ZipInfo(name, date_time=DATE)
    zi.compress_type = zipfile.ZIP_STORED
    zi.external_attr = 0o100644 << 16
    archive.writestr(zi, payload)


def create_backup(workspace, output):
    root, raw_manifest, rows, metadata = _index(workspace)
    dest = Path(output).expanduser().absolute()
    if dest.suffix.lower() != ".zip" or dest.is_symlink() or dest.exists():
        raise FileExistsError("backup output must be a new ZIP")
    if dest == root or root in dest.parents:
        raise ValueError("backup must be outside the Creator workspace")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("xb") as stream:
        try:
            with zipfile.ZipFile(stream, "w") as archive:
                _entry(archive, "manifest.json", raw_manifest)
                for row in rows:
                    data = (root / row["path"]).read_bytes()
                    if len(data) != row["bytes"] or _hash(data) != row["sha256"]:
                        raise ValueError("Creator audio changed during backup")
                    _entry(archive, row["path"], data)
                if _filehash(root / "manifest.json") != metadata["manifest_sha256"]:
                    raise ValueError("Creator manifest changed during backup")
                info = json.dumps(metadata, ensure_ascii=False, sort_keys=True,
                                  indent=2).encode("utf-8") + b"\n"
                _entry(archive, "backup-index.json", info)
        except BaseException:
            stream.close()
            dest.unlink(missing_ok=True)
            raise
    try:
        checked = verify_backup(dest)
    except BaseException:
        dest.unlink(missing_ok=True)
        raise
    return {"output": str(dest), "sha256": _filehash(dest),
            "bytes": dest.stat().st_size, **checked}


def _open_verified(path):
    source = Path(path).expanduser()
    if source.is_symlink() or not source.is_file() or source.stat().st_size > MAX_ARCHIVE_BYTES + MAX_MANIFEST_BYTES + 100000:
        raise ValueError("backup missing, symlink or exceeds 256 MiB")
    archive = zipfile.ZipFile(source)
    try:
        entries = archive.infolist()
        names = [e.filename for e in entries]
        if not 3 <= len(entries) <= MAX_CLIPS + 2 or len(set(names)) != len(names):
            raise ValueError("invalid Creator backup member count or duplicate paths")
        if names[0] != "manifest.json" or names[-1] != "backup-index.json":
            raise ValueError("backup missing manifest or index")
        if any(e.compress_type != zipfile.ZIP_STORED or e.flag_bits & 1 for e in entries):
            raise ValueError("unsupported compressed or encrypted Creator backup")
        if entries[-1].file_size > MAX_MANIFEST_BYTES or entries[0].file_size > MAX_MANIFEST_BYTES:
            raise ValueError("Creator backup metadata exceeds size limit")
        try:
            metadata = json.loads(archive.read("backup-index.json").decode("utf-8"),
                                  object_pairs_hook=_no_duplicate_keys)
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"),
                                  object_pairs_hook=_no_duplicate_keys)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid backup manifest/index JSON") from exc
        if not isinstance(metadata, dict) or set(metadata) != {
            "schema", "pack_id", "manifest_sha256", "audio", "audio_count",
            "total_source_bytes", "source_rights_independently_verified",
            "independent_device_verified", "install_authorized",
        } or metadata["schema"] != SCHEMA:
            raise ValueError("backup index schema invalid")
        if any(metadata[k] is not False for k in (
                "source_rights_independently_verified", "independent_device_verified",
                "install_authorized")):
            raise ValueError("backup may not assert rights or hardware verification")
        if not isinstance(manifest, dict) or manifest.get("schema") != "vvh.voicepack.v1" or manifest.get("id") != metadata["pack_id"]:
            raise ValueError("backup Creator manifest identity mismatch")
        if not isinstance(metadata["manifest_sha256"], str) or _hash(archive.read("manifest.json")) != metadata["manifest_sha256"]:
            raise ValueError("Creator backup manifest checksum mismatch")
        rows = metadata["audio"]
        if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_CLIPS:
            raise ValueError("backup audio index size invalid")
        if not isinstance(manifest.get("events"), dict):
            raise ValueError("backup Creator events missing")
        expected = sorted(set(manifest["events"].values()))
        if expected != [r.get("path") for r in rows if isinstance(r, dict)]:
            raise ValueError("backup audio assignment mismatch")
        if names[1:-1] != expected:
            raise ValueError("backup archive contains extra, missing or unsorted members")
        total = entries[0].file_size
        for info, row in zip(entries[1:-1], rows):
            if not isinstance(row, dict) or set(row) != {"path","bytes","sha256"}:
                raise ValueError("invalid backup audio row")
            rel = row["path"]
            if not isinstance(rel, str) or not AUDIO_PATH.fullmatch(rel):
                raise ValueError("backup contains unsafe audio filename")
            if type(row["bytes"]) is not int or not 0 < row["bytes"] <= MAX_AUDIO_BYTES or info.file_size != row["bytes"]:
                raise ValueError("backup audio length mismatch")
            sha = row["sha256"]
            if not isinstance(sha, str) or not SHA.fullmatch(sha):
                raise ValueError("backup audio hash invalid")
            total += row["bytes"]
            if total > MAX_ARCHIVE_BYTES:
                raise ValueError("backup exceeds 256 MiB audio bound")
            digest = hashlib.sha256()
            with archive.open(info) as stream:
                while block := stream.read(65536):
                    digest.update(block)
            if digest.hexdigest() != sha:
                raise ValueError("backup audio checksum mismatch")
        if metadata["audio_count"] != len(rows) or metadata["total_source_bytes"] != total:
            raise ValueError("backup byte totals mismatch")
        return archive, metadata
    except BaseException:
        archive.close()
        raise


def verify_backup(path):
    with _open_verified(path)[0] as archive:
        index = json.loads(archive.read("backup-index.json"))
    return {"schema": SCHEMA, "pack_id": index["pack_id"],
            "audio_count": index["audio_count"],
            "total_source_bytes": index["total_source_bytes"],
            "integrity_verified": True, "install_authorized": False,
            "independent_device_verified": False,
            "redistribution_rights_verified": False}


def restore_backup(path, output_dir):
    with _open_verified(path)[0] as archive:
        target = Path(output_dir).expanduser().absolute()
        if target.exists() or target.is_symlink():
            raise FileExistsError("restore destination must be a new directory")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.mkdir(exist_ok=False)
        try:
            for item in archive.infolist()[:-1]:
                dest = target / item.filename
                dest.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(item) as source, dest.open("xb") as output:
                    shutil.copyfileobj(source, output, length=65536)
            checked = validate_workspace(target)
            if not checked["ok"]:
                raise ValueError("restored Creator workspace invalid")
            restored = _index(target)[3]
            original = json.loads(archive.read("backup-index.json"))
            if restored != original:
                raise ValueError("restored audio/manifest checksums differ")
        except BaseException:
            shutil.rmtree(target)
            raise
    return {"schema": SCHEMA, "workspace": str(target),
            "pack_id": restored["pack_id"],
            "restored_clips": len(restored["audio"]),
            "recovery_verified": True, "original_workspace_modified": False,
            "install_authorized": False, "redistribution_rights_verified": False}


def compare_backup(path, workspace):
    with _open_verified(path)[0] as archive:
        expected = json.loads(archive.read("backup-index.json"))
    _, _, _, current = _index(workspace)
    return {"schema": SCHEMA, "pack_id": expected["pack_id"],
            "matches_backup": current == expected,
            "manifest_changed": current["manifest_sha256"] != expected["manifest_sha256"],
            "audio_changed": current["audio"] != expected["audio"],
            "source_files_modified": False,
            "install_authorized": False}
