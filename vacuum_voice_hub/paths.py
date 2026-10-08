from pathlib import Path

def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent

def catalog_dir() -> Path:
    dev=repo_root() / "catalog"
    return dev if dev.exists() else Path(__file__).resolve().parent / "data"

def cache_dir() -> Path:
    p = Path.home() / ".cache" / "vacuum-voice-hub"
    p.mkdir(parents=True, exist_ok=True)
    return p
