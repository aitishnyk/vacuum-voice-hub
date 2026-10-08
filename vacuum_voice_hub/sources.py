import hashlib, urllib.request
from pathlib import Path
from .paths import cache_dir

UA = "VacuumVoiceHub/0.1 (+https://github.com/aitishnyk/vacuum-voice-hub)"

def git_blob_sha1(path: Path) -> str:
    data=path.read_bytes(); h=hashlib.sha1(); h.update(f"blob {len(data)}\0".encode()); h.update(data); return h.hexdigest()

def verify(path: Path, source: dict):
    if path.stat().st_size != int(source["size"]):
        raise ValueError(f"size mismatch: got {path.stat().st_size}, expected {source['size']}")
    if source.get("git_blob_sha1") and git_blob_sha1(path).lower()!=source["git_blob_sha1"].lower():
        raise ValueError("Git blob SHA-1 mismatch")
    if source.get("md5"):
        md5=hashlib.md5(path.read_bytes()).hexdigest()
        if md5.lower()!=source["md5"].lower(): raise ValueError("MD5 mismatch")
    return True

def fetch(voice: dict) -> Path:
    src=voice["source"]
    ext=".tar.gz" if ".tar.gz" in src["url"] or src["url"].endswith((".gz","pensive")) else Path(src["url"]).suffix
    dst=cache_dir()/f"{voice['id']}{ext}"
    if dst.exists():
        try: verify(dst,src); return dst
        except Exception: dst.unlink(missing_ok=True)
    req=urllib.request.Request(src["url"],headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=45) as r, open(dst,"wb") as f:
        while True:
            chunk=r.read(1024*256)
            if not chunk: break
            f.write(chunk)
    verify(dst,src)
    return dst
