import tempfile
from pathlib import Path
from .catalog import voice_by_id, model_by_id, event_profile_for_model
from .sources import fetch
from .formats.registry import get as get_format
from .models.registry import get as get_model
from .paths import cache_dir
from .compatibility import report_dir, merge_fallback

def _adapt(voice, work: Path):
    source=fetch(voice)
    return get_format(voice["format"])(source,work)

def build_voice(voice_id, model_id, fallback_voice_id=None):
    voice=voice_by_id(voice_id); model_by_id(model_id)
    if fallback_voice_id == voice_id:
        raise ValueError("fallback voice must be different from primary voice")
    outdir=cache_dir()/"builds"; outdir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vvh-") as td:
        work=Path(td)
        converted=_adapt(voice,work/"primary")
        original_report=report_dir(converted["dir"],model_id)
        fallback_meta=None
        if fallback_voice_id:
            fallback_voice=voice_by_id(fallback_voice_id)
            fallback_converted=_adapt(fallback_voice,work/"fallback")
            fallback_report=report_dir(fallback_converted["dir"],model_id)
            added=merge_fallback(converted["dir"],fallback_converted["dir"],model_id)
            fallback_meta={
                "voice_id":fallback_voice_id,
                "added_events":len(added),
                "added_ids":added,
                "coverage":fallback_report,
            }
        final_report=report_dir(converted["dir"],model_id)
        target=outdir/f"{voice_id}__{model_id.replace('.','_')}.tar.gz"
        profile=event_profile_for_model(model_id)
        meta=get_model(model_id).package(converted["dir"],target,allowed_ids=set(profile["known_event_ids"]))
    return {
        "voice":voice,
        "model":model_id,
        "source_events":converted.get("source_events",converted.get("events")),
        "compatibility":final_report,
        "original_compatibility":original_report,
        "fallback":fallback_meta,
        **meta,
    }
