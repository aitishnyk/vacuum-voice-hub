from pathlib import Path
from .catalog import event_profile_for_model, event_by_id, categories as catalog_categories

def event_ids(canonical_dir: Path):
    out=set()
    for p in Path(canonical_dir).glob("*.ogg"):
        try:
            out.add(int(p.stem))
        except ValueError:
            pass
    return out

def _category_summary(ids,known):
    result={}
    for category in catalog_categories():
        category_known={i for i in known if event_by_id(i).get("category","other")==category}
        if not category_known:
            continue
        covered=set(ids)&category_known
        result[category]={
            "known":len(category_known),
            "covered":len(covered),
            "missing":len(category_known-covered),
            "coverage_pct":round(len(covered)/len(category_known)*100,1),
        }
    return result

def report_dir(canonical_dir: Path, model_id: str):
    profile=event_profile_for_model(model_id)
    known=set(profile["known_event_ids"])
    core=set(profile.get("core_event_ids",[]))
    available=event_ids(Path(canonical_dir))
    covered=available&known
    missing=known-available
    extra=available-known
    core_covered=available&core
    core_missing=core-available
    coverage=round((len(covered)/len(known))*100,1) if known else 0.0
    core_coverage=round((len(core_covered)/len(core))*100,1) if core else 0.0
    if coverage>=95 and core_coverage>=95:
        grade="excellent"
    elif coverage>=80 and core_coverage>=85:
        grade="strong"
    elif coverage>=50:
        grade="partial"
    else:
        grade="low"
    return {
        "profile":profile["id"],
        "profile_kind":profile.get("profile_kind"),
        "profile_hardware_verified":bool(profile.get("hardware_verified")),
        "known_total":len(known),
        "source_events":len(available),
        "covered":len(covered),
        "missing":len(missing),
        "extra":len(extra),
        "coverage_pct":coverage,
        "core_total":len(core),
        "core_covered":len(core_covered),
        "core_missing":len(core_missing),
        "core_coverage_pct":core_coverage,
        "grade":grade,
        "category_coverage":_category_summary(available,known),
        "covered_ids":sorted(covered),
        "missing_ids":sorted(missing),
        "extra_ids":sorted(extra),
        "missing_core_events":[
            {
                "id":i,
                "semantic":event_by_id(i).get("semantic"),
                "category":event_by_id(i).get("category"),
                "description":event_by_id(i).get("description"),
            }
            for i in sorted(core_missing)
        ],
    }

def merge_fallback(primary_dir: Path, fallback_dir: Path, model_id: str, categories=None):
    profile=event_profile_for_model(model_id)
    known=set(profile["known_event_ids"])
    primary=event_ids(primary_dir)
    fallback=event_ids(fallback_dir)
    categories=set(categories or [])
    candidates=(known-primary)&fallback
    if categories:
        candidates={i for i in candidates if event_by_id(i).get("category","other") in categories}
    added=[]
    for event_id in sorted(candidates):
        src=Path(fallback_dir)/f"{event_id}.ogg"
        dst=Path(primary_dir)/f"{event_id}.ogg"
        dst.write_bytes(src.read_bytes())
        added.append(event_id)
    return added
