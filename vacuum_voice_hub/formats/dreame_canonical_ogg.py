import re
from pathlib import Path
from ..archive import extract
from ..audio import normalize

def adapt(source: Path, work: Path) -> dict:
    raw=work/"raw"; out=work/"canonical"; extract(source,raw); out.mkdir(parents=True,exist_ok=True)
    found={}
    for f in raw.rglob("*.ogg"):
        m=re.fullmatch(r"(\d+)\.ogg",f.name)
        if m and m.group(1) not in found: found[m.group(1)]=f
    if len(found)<5: raise ValueError(f"only {len(found)} numbered ogg files")
    for event,src in found.items(): normalize(src,out/f"{int(event)}.ogg","ogg")
    return {"dir":out,"events":len(found)}
