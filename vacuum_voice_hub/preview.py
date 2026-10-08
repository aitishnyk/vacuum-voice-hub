import tempfile
from pathlib import Path
from .catalog import voice_by_id,event_profile_for_model
from .sources import fetch
from .formats.registry import get as get_format
from .paths import cache_dir

def preview_file(voice_id,model_id="dreame.vacuum.r2209",preferred=(7,11,13,18,45)):
    voice=voice_by_id(voice_id)
    profile=event_profile_for_model(model_id)
    known=set(profile["known_event_ids"])
    with tempfile.TemporaryDirectory(prefix="vvh-preview-") as td:
        work=Path(td)
        source=fetch(voice)
        converted=get_format(voice["format"])(source,work)
        files={}
        for p in Path(converted["dir"]).glob("*.ogg"):
            try:event_id=int(p.stem)
            except ValueError:continue
            if event_id in known:files[event_id]=p
        if not files:raise ValueError("no compatible canonical OGG events for preview")
        chosen=next((e for e in preferred if e in files),None)
        if chosen is None:chosen=sorted(files)[0]
        out=cache_dir()/"previews"/voice_id
        out.mkdir(parents=True,exist_ok=True)
        dst=out/f"{model_id.replace('.','_')}__{chosen}.ogg"
        dst.write_bytes(files[chosen].read_bytes())
        return dst
