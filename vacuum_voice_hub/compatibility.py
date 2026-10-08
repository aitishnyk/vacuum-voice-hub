from pathlib import Path
from .catalog import event_profile_for_model

def _ids(canonical_dir: Path):
    out=set()
    for p in Path(canonical_dir).glob("*.ogg"):
        try: out.add(int(p.stem))
        except ValueError: pass
    return out

def report_dir(canonical_dir: Path, model_id: str):
    profile=event_profile_for_model(model_id)
    known=set(profile["known_event_ids"])
    core=set(profile.get("core_event_ids",[]))
    available=_ids(Path(canonical_dir))
    covered=available & known
    missing=known - available
    extra=available - known
    core_covered=available & core
    core_missing=core - available
    coverage=round((len(covered)/len(known))*100,1) if known else 0.0
    core_coverage=round((len(core_covered)/len(core))*100,1) if core else 0.0
    if coverage >= 95 and core_coverage >= 95: grade="excellent"
    elif coverage >= 80 and core_coverage >= 85: grade="strong"
    elif coverage >= 50: grade="partial"
    else: grade="low"
    return {
        "profile":profile["id"],
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
        "covered_ids":sorted(covered),
        "missing_ids":sorted(missing),
        "extra_ids":sorted(extra),
    }

def merge_fallback(primary_dir: Path, fallback_dir: Path, model_id: str):
    profile=event_profile_for_model(model_id)
    known=set(profile["known_event_ids"])
    primary=_ids(primary_dir)
    fallback=_ids(fallback_dir)
    added=[]
    for event_id in sorted((known-primary) & fallback):
        src=Path(fallback_dir)/f"{event_id}.ogg"
        dst=Path(primary_dir)/f"{event_id}.ogg"
        dst.write_bytes(src.read_bytes())
        added.append(event_id)
    return added
