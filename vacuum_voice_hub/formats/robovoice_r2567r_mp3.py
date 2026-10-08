import re
from pathlib import Path
from ..archive import extract
from ..audio import normalize
from ..catalog import bridge

def adapt(source: Path, work: Path) -> dict:
    raw=work/"raw"; out=work/"canonical"; extract(source,raw); out.mkdir(parents=True,exist_ok=True)
    found={}
    for f in raw.rglob("*.mp3"):
        m=re.fullmatch(r"(\d{3})\.mp3",f.name)
        if m and m.group(1) not in found: found[m.group(1)]=f
    if len(found)<5: raise ValueError(f"only {len(found)} NNN.mp3 files")
    used=[]
    for src_id,target in bridge().items():
        if src_id not in found: continue
        dst=out/f"{int(target)}.ogg"
        if dst.exists(): continue
        normalize(found[src_id],dst,"ogg"); used.append((src_id,int(target)))
    if len(used)<5: raise ValueError("too few mapped events")
    return {"dir":out,"events":len(used),"source_events":len(found)}
