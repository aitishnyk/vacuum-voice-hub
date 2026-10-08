import os,sys
from pathlib import Path

def repo_root()->Path:
    return Path(__file__).resolve().parent.parent

def catalog_dir()->Path:
    dev=repo_root()/"catalog"
    return dev if dev.exists() else Path(__file__).resolve().parent/"data"

def cache_dir()->Path:
    p=Path.home()/".cache"/"vacuum-voice-hub"
    p.mkdir(parents=True,exist_ok=True)
    return p

def data_dir()->Path:
    override=os.environ.get("VVH_DATA_DIR")
    if override:
        p=Path(override).expanduser()
    elif sys.platform=="darwin":
        p=Path.home()/"Library"/"Application Support"/"VacuumVoiceHub"
    elif os.name=="nt":
        p=Path(os.environ.get("LOCALAPPDATA",Path.home()))/"VacuumVoiceHub"
    else:
        p=Path(os.environ.get("XDG_DATA_HOME",Path.home()/".local"/"share"))/"vacuum-voice-hub"
    p.mkdir(parents=True,exist_ok=True)
    return p

def creator_dir()->Path:
    p=data_dir()/"creator"
    p.mkdir(parents=True,exist_ok=True)
    return p
