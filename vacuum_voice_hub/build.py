import tempfile
from pathlib import Path
from .catalog import voice_by_id, model_by_id
from .sources import fetch
from .formats.registry import get as get_format
from .models.registry import get as get_model
from .paths import cache_dir

def build_voice(voice_id, model_id):
    voice=voice_by_id(voice_id); model_by_id(model_id)
    source=fetch(voice)
    outdir=cache_dir()/"builds"; outdir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vvh-") as td:
        work=Path(td)
        converted=get_format(voice["format"])(source,work)
        target=outdir/f"{voice_id}__{model_id.replace('.','_')}.tar.gz"
        meta=get_model(model_id).package(converted["dir"],target)
    return {"voice":voice,"model":model_id,**meta}
