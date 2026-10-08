#!/usr/bin/env python3
from collections import Counter
import json
from pathlib import Path
from vacuum_voice_hub.catalog import models,voices,event_profile_for_model,model_by_id
from vacuum_voice_hub.models.registry import get as get_model

mm=models();vv=voices()
ids=[m["id"] for m in mm]
assert len(ids)==len(set(ids))
baseline=json.loads((Path(__file__).resolve().parents[1]/"tests"/"fixtures"/"v08_model_identity.json").read_text())
assert baseline["model_count"]==109
for old in baseline["models"]:
    assert model_by_id(old["id"])["id"]==old["id"],("lost base model",old["id"])
    for alias in old["aliases"]:
        assert model_by_id(alias)["id"]==old["id"],("base alias changed",alias)
aliases={}
for model in mm:
    for alias in model.get("aliases",[]):
        owner=aliases.setdefault(alias,model["id"])
        assert owner==model["id"],("duplicate alias",alias,owner,model["id"])
assert len(mm)==154,(len(mm),"models")
assert len(vv)==55,(len(vv),"voices")
assert sum(bool(m.get("device_tested")) for m in mm)==1
counts=Counter(m["adapter"] for m in mm)
expected={"dreame_numeric":51,"roborock_legacy":33,"ijai_zip":8,"semantic_bundle":62}
assert dict(counts)==expected,(counts,expected)
for m in mm:
    profile=event_profile_for_model(m["id"])
    assert profile["known_count"]==len(profile["known_event_ids"])
    assert len(profile["known_event_ids"])>=5
    adapter=get_model(m["id"])
    assert callable(adapter.package)
    assert getattr(adapter,"OUTPUT_SUFFIX",None)
    t=m.get("transport",{})
    if t.get("kind") in {"signed-official-only","unsupported-local"}:
        assert not t.get("allow_default")
print(f"MODEL MATRIX PASS: {len(mm)} models × {len(vv)} voices = {len(mm)*len(vv)} target combinations")
print("Adapters:",dict(counts))
