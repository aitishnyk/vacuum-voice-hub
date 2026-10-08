import tempfile
from pathlib import Path
from .catalog import voice_by_id, model_by_id, event_profile_for_model
from .sources import fetch
from .formats.registry import get as get_format
from .models.registry import get as get_model
from .paths import cache_dir
from .compatibility import report_dir, merge_fallback

def _adapt(voice,work:Path):
    work.mkdir(parents=True,exist_ok=True)
    source=fetch(voice)
    return get_format(voice["format"])(source,work)

def _parse_fallback_plan(fallback_voice_id=None,fallback_categories=None):
    plan=[]
    if fallback_categories:
        for category,voice_id in fallback_categories.items():
            if voice_id:
                plan.append({"voice_id":voice_id,"categories":[category]})
    if fallback_voice_id:
        plan.append({"voice_id":fallback_voice_id,"categories":[]})
    return plan

def build_voice(voice_id,model_id,fallback_voice_id=None,fallback_categories=None,package_output=True):
    voice=voice_by_id(voice_id)
    model=model_by_id(model_id)
    if fallback_voice_id==voice_id:
        raise ValueError("fallback voice must be different from primary voice")
    for category,fallback_id in (fallback_categories or {}).items():
        if fallback_id==voice_id:
            raise ValueError(f"fallback for {category} must differ from primary voice")
    outdir=cache_dir()/"builds"
    outdir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vvh-") as td:
        work=Path(td)
        converted=_adapt(voice,work/"primary")
        original_report=report_dir(converted["dir"],model["id"])
        fallback_meta=[]
        for index,item in enumerate(_parse_fallback_plan(fallback_voice_id,fallback_categories)):
            fallback_voice=voice_by_id(item["voice_id"])
            fallback_converted=_adapt(fallback_voice,work/f"fallback-{index}")
            fallback_report=report_dir(fallback_converted["dir"],model["id"])
            added=merge_fallback(
                converted["dir"],
                fallback_converted["dir"],
                model["id"],
                categories=item["categories"],
            )
            fallback_meta.append({
                "voice_id":item["voice_id"],
                "categories":item["categories"] or ["*"],
                "added_events":len(added),
                "added_ids":added,
                "coverage":fallback_report,
            })
        final_report=report_dir(converted["dir"],model["id"])
        target=outdir/f"{voice_id}__{model['id'].replace('.','_')}.tar.gz"
        profile=event_profile_for_model(model["id"])
        meta=get_model(model["id"]).package(
            converted["dir"],
            target,
            allowed_ids=set(profile["known_event_ids"]),
        )
    return {
        "voice":voice,
        "model":model["id"],
        "requested_model":model_id,
        "source_events":converted.get("source_events",converted.get("events")),
        "compatibility":final_report,
        "original_compatibility":original_report,
        "fallbacks":fallback_meta,
        **meta,
    }
