"""Bounded, fail-closed extraction for local voice pack imports.

Do not delegate to tar.extractall(): Python 3.10/3.11 have no uniform
safe extraction filter. Refuse links, special members and ambiguous paths.
"""
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

MAX_INPUT_BYTES = 256 * 1024 * 1024
MAX_FILES = 4096
MAX_MEMBER_BYTES = 32 * 1024 * 1024
MAX_UNPACKED_BYTES = 256 * 1024 * 1024


def _safe(name):
    """Retained compatibility helper; true only for portable relative members."""
    try:
        _member_name(name)
        return True
    except ValueError:
        return False


def _member_name(name):
    if not isinstance(name, str) or not name or len(name) > 512:
        raise ValueError("unsafe archive member name")
    if "\\" in name or ":" in name or not name.isprintable() or name.startswith("/"):
        raise ValueError(f"unsafe archive member: {name!r}")
    # Common tar convention ./name is okay; internal dot/traversal is not.
    while name.startswith("./"):
        name = name[2:]
    name = name.rstrip("/")
    pieces = name.split("/")
    if not name or any(part in ("", ".", "..") for part in pieces):
        raise ValueError(f"unsafe archive member: {name!r}")
    return PurePosixPath(*pieces)


def _preflight(records):
    total = 0
    seen = set()
    paths = set()
    files = []
    if len(records) > MAX_FILES * 2:
        raise ValueError("archive member count exceeds limit")
    for raw_name, size, is_dir, item in records:
        path = _member_name(raw_name)
        folded = path.as_posix().casefold()
        if folded in seen:
            raise ValueError(f"duplicate archive member: {raw_name!r}")
        seen.add(folded)
        if is_dir:
            paths.add((path.as_posix(), True))
            continue
        if type(size) is not int or size < 0 or size > MAX_MEMBER_BYTES:
            raise ValueError("oversized or invalid archive member")
        total += size
        if total > MAX_UNPACKED_BYTES or len(files) >= MAX_FILES:
            raise ValueError("archive decompressed-size or file-count limit exceeded")
        files.append((path, size, item))
        paths.add((path.as_posix(), False))
    regular = {p.as_posix() for p, _, _ in files}
    for path, _, _ in files:
        if any(parent.as_posix() in regular for parent in path.parents if parent.as_posix() != "."):
            raise ValueError("file/directory collision in archive")
    if any(p in regular for p, is_dir in paths if is_dir):
        raise ValueError("file/directory collision in archive")
    return files


def _copy_file(source, dest, expected, root):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.parent.resolve().is_relative_to(root):
        raise ValueError("unsafe archive destination")
    with dest.open("xb") as output:
        count = 0
        while count < expected:
            chunk = source.read(min(65536, expected - count))
            if not chunk:
                raise ValueError("truncated archive member")
            count += len(chunk)
            output.write(chunk)
        # Do not trust an overlong stream even when header declares less data.
        if source.read(1):
            raise ValueError("archive member exceeds declared size")


def extract(src: Path, dst: Path):
    """Extract only bounded regular files from tar or ZIP into a local directory."""
    src = Path(src)
    dst = Path(dst)
    if not src.is_file() or src.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("missing or oversized archive")
    dst.mkdir(parents=True, exist_ok=True)
    root = dst.resolve()

    if tarfile.is_tarfile(src):
        with tarfile.open(src, "r:*") as archive:
            records = []
            for item in archive:
                if not item.isfile() and not item.isdir():
                    raise ValueError(f"unsafe archive member: {item.name!r}")
                records.append((item.name, item.size, item.isdir(), item))
                if len(records) > MAX_FILES * 2:
                    raise ValueError("archive member count exceeds limit")
            files = _preflight(records)
            for name, size, item in files:
                stream = archive.extractfile(item)
                if stream is None:
                    raise ValueError("archive member has no data")
                with stream:
                    _copy_file(stream, root / name, size, root)
        return

    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as archive:
            records = []
            for item in archive.infolist():
                mode = (item.external_attr >> 16) & 0o170000
                if item.flag_bits & 1 or mode not in (0, 0o100000, 0o040000):
                    raise ValueError(f"unsafe archive member: {item.filename!r}")
                if item.is_dir() and mode == 0o100000:
                    raise ValueError(f"invalid ZIP directory: {item.filename!r}")
                if not item.is_dir() and mode == 0o040000:
                    raise ValueError(f"invalid ZIP file: {item.filename!r}")
                records.append((item.filename, item.file_size, item.is_dir(), item))
                if len(records) > MAX_FILES * 2:
                    raise ValueError("archive member count exceeds limit")
            files = _preflight(records)
            for name, size, item in files:
                with archive.open(item, "r") as stream:
                    _copy_file(stream, root / name, size, root)
        return

    raise ValueError("unsupported archive")
