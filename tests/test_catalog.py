import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def _voices():
    return json.loads((ROOT/"catalog/voices.json").read_text())["voices"]

def test_catalog_unique_ids_and_v02_scale():
    vv=_voices(); ids=[x["id"] for x in vv]
    assert len(ids)==len(set(ids))
    assert len(ids)>=50
    assert len({x["language"] for x in vv})>=7

def test_every_voice_has_credit_source_and_integrity_metadata():
    for v in _voices():
        assert v.get("credit")
        assert v.get("source",{}).get("page")
        assert v.get("source",{}).get("url")
        assert v.get("source",{}).get("size",0)>0
        assert v.get("source_verification") in {"git-blob+size","git-blob+md5+size","release-md5+size","md5+size","metadata-only"}
        assert v.get("content_rating") in {"general","explicit"}
        assert isinstance(v.get("adult"),bool)
        assert v.get("origin_model")

def test_explicit_labels_are_consistent():
    for v in _voices():
        if v["content_rating"]=="explicit":
            assert v["adult"] is True

def test_model_r2209_present_with_event_profile():
    d=json.loads((ROOT/"catalog/models.json").read_text())
    m=next(x for x in d["models"] if x["id"]=="dreame.vacuum.r2209")
    assert m["device_tested"] is True
    assert m["event_profile"]=="x10-known-v1"
