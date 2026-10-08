import re
from pathlib import Path
from ..archive import extract
from ..audio import normalize
from ..catalog import bridge, ijai_map

def adapt(source: Path, work: Path) -> dict:
    raw=work/"raw"; out=work/"canonical"; extract(source,raw); out.mkdir(parents=True,exist_ok=True)
    files={f.name:f for f in raw.rglob("*.mp3")}
    if len(files)<5: raise ValueError(f"only {len(files)} mp3 files")
    b=bridge(); used=[]
    for rid,name in ijai_map().items():
        src=files.get(name)
        if not src or rid not in b: continue
        target=int(b[rid]); dst=out/f"{target}.ogg"
        if dst.exists(): continue
        normalize(src,dst,"ogg"); used.append((rid,name,target))
    if len(used)<5: raise ValueError(f"only {len(used)} named events mapped")
    return {"dir":out,"events":len(used),"source_events":len(files)}
