import tarfile, zipfile
from pathlib import Path

def _safe(name):
    p=Path(name)
    return not p.is_absolute() and ".." not in p.parts

def extract(src: Path, dst: Path):
    dst.mkdir(parents=True,exist_ok=True)
    if tarfile.is_tarfile(src):
        with tarfile.open(src,"r:*") as tf:
            for m in tf.getmembers():
                if not _safe(m.name) or m.issym() or m.islnk(): raise ValueError(f"unsafe archive member: {m.name}")
            try: tf.extractall(dst,filter="data")
            except TypeError: tf.extractall(dst)
        return
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if not _safe(n): raise ValueError(f"unsafe archive member: {n}")
            z.extractall(dst)
        return
    raise ValueError("unsupported archive")
