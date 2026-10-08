import tarfile
from pathlib import Path
from .build import build_voice
from .paths import cache_dir

def preview_file(voice_id, model_id="dreame.vacuum.r2209", preferred=(7,11,13,18,45)):
    built=build_voice(voice_id,model_id); src=Path(built["path"]); out=cache_dir()/"previews"/voice_id; out.mkdir(parents=True,exist_ok=True)
    with tarfile.open(src,"r:gz") as tf:
        names={Path(n).name:n for n in tf.getnames()}
        chosen=None
        for e in preferred:
            if f"{e}.ogg" in names: chosen=f"{e}.ogg"; break
        if not chosen:
            chosen=next((n for n in names if n.endswith('.ogg')),None)
        if not chosen: raise ValueError("no OGG in built package")
        f=tf.extractfile(names[chosen]); data=f.read(); dst=out/chosen; dst.write_bytes(data); return dst
