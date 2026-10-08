from pathlib import Path
from ..audio import normalize
from ..catalog import roborock_map

def adapt_dir(raw: Path, out: Path) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    files={f.name.lower():f for f in raw.rglob('*') if f.is_file()}
    used=[]
    for event,name in roborock_map().items():
        src=files.get(name.lower())
        if not src: continue
        dst=out/f"{int(event)}.ogg"
        if dst.exists(): continue
        normalize(src,dst,"ogg"); used.append((name,int(event)))
    if len(used)<5: raise ValueError(f"only {len(used)} Roborock named events mapped")
    return {"dir":out,"events":len(used),"source_events":len(files)}
