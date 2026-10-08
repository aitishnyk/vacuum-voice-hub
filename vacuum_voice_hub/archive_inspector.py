"""Bounded offline voice archive inventory for transport research.

Read-only metadata and hashes: never extract, execute or install an archive.
"""
import hashlib
import json
import re
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_FILES = 512
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
CHUNK = 64 * 1024
AUDIO_EXTENSIONS = {".ogg", ".mp3", ".wav", ".flac"}
SAFE_NAME = re.compile(r"^[A-Za-z0-9._/ -]+$")


class ArchiveInspectionError(ValueError):
    pass


def _safe_name(raw):
    if not isinstance(raw, str) or not raw or len(raw) > 240 or "\\" in raw:
        raise ArchiveInspectionError("unsafe member name")
    name = PurePosixPath(raw)
    if raw.startswith("/") or any(part in ("", ".", "..") for part in raw.split("/")):
        raise ArchiveInspectionError("unsafe member path")
    if not SAFE_NAME.fullmatch(raw) or ":" in raw:
        raise ArchiveInspectionError("unsupported member path")
    return name.as_posix()


def _digest(reader, expected):
    h = hashlib.sha256()
    length = 0
    while True:
        block = reader.read(min(CHUNK, expected - length + 1))
        if not block:
            break
        length += len(block)
        if length > expected or length > MAX_FILE_BYTES:
            raise ArchiveInspectionError("member exceeds declared size")
        h.update(block)
    if length != expected:
        raise ArchiveInspectionError("member size mismatch")
    return h.hexdigest()


def inspect_archive(path):
    """Inventory a ZIP or tar.gz without extracting files to disk.

    Bounds apply both to archive metadata and bytes actually read.
    Any special files, links, encrypted ZIP members or colliding paths fail closed.
    """
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ArchiveInspectionError("missing or oversized archive")
    files = []
    seen = set()
    total = 0

    def add(name, size, opener):
        nonlocal total
        safe = _safe_name(name)
        folded = safe.casefold()
        if folded in seen:
            raise ArchiveInspectionError("duplicate or case-colliding archive path")
        seen.add(folded)
        if type(size) is not int or size < 0 or size > MAX_FILE_BYTES:
            raise ArchiveInspectionError("invalid or oversized member")
        total += size
        if total > MAX_TOTAL_BYTES or len(files) >= MAX_FILES:
            raise ArchiveInspectionError("archive inventory limit exceeded")
        with opener() as stream:
            digest = _digest(stream, size)
        files.append({"path": safe, "size_bytes": size, "sha256": digest,
                      "audio": PurePosixPath(safe).suffix.lower() in AUDIO_EXTENSIONS})

    try:
        if zipfile.is_zipfile(path):
            kind = "zip"
            with zipfile.ZipFile(path) as archive:
                for item in archive.infolist():
                    if item.is_dir():
                        continue
                    mode = (item.external_attr >> 16) & 0o170000
                    if item.flag_bits & 1 or mode not in (0, 0o100000):
                        raise ArchiveInspectionError("encrypted or special ZIP member")
                    add(item.filename, item.file_size, lambda item=item: archive.open(item))
        elif tarfile.is_tarfile(path):
            kind = "tar"
            with tarfile.open(path, mode="r:*") as archive:
                for item in archive:
                    if item.isdir():
                        continue
                    if not item.isfile():
                        raise ArchiveInspectionError("special tar member")
                    add(item.name, item.size, lambda item=item: archive.extractfile(item))
        else:
            raise ArchiveInspectionError("unsupported archive format")
    except (zipfile.BadZipFile, tarfile.TarError, EOFError, OSError, RuntimeError) as exc:
        raise ArchiveInspectionError("archive is damaged or unreadable") from exc
    return {
        "schema": "vvh.archive-inventory.v1",
        "container": kind,
        "install_authorized": False,
        "hardware_verified": False,
        "file_count": len(files),
        "audio_count": sum(row["audio"] for row in files),
        "files": files,
    }


def inspect_to_json(path):
    return json.dumps(inspect_archive(path), sort_keys=True, indent=2) + "\n"
