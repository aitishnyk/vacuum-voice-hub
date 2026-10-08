import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_semantic_event_union_and_namespace():
    doc=json.loads((ROOT/"catalog/events.json").read_text())
    assert doc["schema"]==2
    assert doc["semantic_namespace"]=="vvh.semantic.v1"
    events=doc["events"]
    assert len(events)>=560
    ids=[e["id"] for e in events]
    assert len(ids)==len(set(ids))
    by_id={e["id"]:e for e in events}
    assert by_id[7]["semantic"]=="clean.start"
    assert by_id[35]["semantic"]=="error.main_brush"
    assert by_id[45]["semantic"]=="locate.here"

def test_event_profiles_have_provenance():
    doc=json.loads((ROOT/"catalog/event_profiles.json").read_text())
    assert len(doc["profiles"])==11
    for p in doc["profiles"]:
        assert p.get("source_evidence")
        assert p.get("profile_kind")
