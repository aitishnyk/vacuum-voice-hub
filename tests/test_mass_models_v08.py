import json
from pathlib import Path
import pytest
from vacuum_voice_hub.catalog import models,voices,model_by_id,event_profile_for_model
from vacuum_voice_hub.models.registry import get as get_model
from vacuum_voice_hub.install import _validate_transport

ROOT=Path(__file__).resolve().parents[1]

def test_v08_mass_model_inventory_complete():
    doc=json.loads((ROOT/"catalog/models.json").read_text())
    assert doc["schema"]==3
    assert doc["expansion"]["requested_inventory_rows"]==103
    assert len(doc["models"])==154
    ids=[m["id"] for m in doc["models"]]
    assert len(ids)==len(set(ids))
    required={
        "roborock.vacuum.a46","dreame.vacuum.r2228","xiaomi.vacuum.d101",
        "mijia.vacuum.b108zb","viomi.vacuum.v49","ijai.vacuum.v2",
        "roidmi.vacuum.v66","xiaomi.vacuum.c102gl","rockrobo.vacuum.v1",
        "roborock.vacuum.a70","roborock.vacuum.s4",
    }
    assert required.issubset(set(ids))

def test_all_models_have_runtime_adapter_and_profile():
    for m in models():
        adapter=get_model(m["id"])
        assert callable(adapter.package)
        assert callable(adapter.make_voice_value)
        profile=event_profile_for_model(m["id"])
        assert len(profile["known_event_ids"])>=5
        assert profile["known_count"]==len(profile["known_event_ids"])

def test_only_x10_remains_hardware_verified():
    verified=[m["id"] for m in models() if m.get("device_tested")]
    assert verified==["dreame.vacuum.r2209"]

def test_family_counts_and_8470_target_matrix():
    mm=models();vv=voices()
    counts={}
    for m in mm:counts[m["adapter"]]=counts.get(m["adapter"],0)+1
    assert counts=={
        "dreame_numeric":51,
        "roborock_legacy":33,
        "ijai_zip":8,
        "semantic_bundle":62,
    }
    assert len(vv)==55
    assert len(mm)*len(vv)==8470

def test_transport_policy_new_families_fail_closed():
    old_robo=model_by_id("roborock.vacuum.s5")
    with pytest.raises(RuntimeError,match="allow-experimental-transport"):
        _validate_transport(old_robo,False)
    assert _validate_transport(old_robo,True)["kind"]=="roborock-miio-sound"

    signed=model_by_id("roborock.vacuum.a70")
    with pytest.raises(RuntimeError,match="vendor-signed"):
        _validate_transport(signed,True)

    ijai=model_by_id("ijai.vacuum.v2")
    with pytest.raises(RuntimeError,match="allow-experimental-transport"):
        _validate_transport(ijai,False)
    assert _validate_transport(ijai,True)["kind"]=="miot-action-url-md5"

    h40=model_by_id("xiaomi.vacuum.d101")
    with pytest.raises(RuntimeError,match="build/coverage-only"):
        _validate_transport(h40,True)

def test_inventory_metadata_is_retained():
    for model_id,product_id,plugin_id in [
        ("xiaomi.vacuum.d101",1020911,9053506),
        ("roborock.vacuum.a46",1007619,8134107),
        ("xiaomi.vacuum.c102gl",1018443,9164458),
        ("dreame.vacuum.r2228o",1010702,8037453),
    ]:
        m=model_by_id(model_id)
        assert m["product_id"]==product_id
        assert m["plugin_id"]==plugin_id
