import json
import pytest
from pathlib import Path
from vacuum_voice_hub.catalog import model_by_id,event_profile_for_model
from vacuum_voice_hub.models.registry import get as get_model
from vacuum_voice_hub.install import _validate_transport

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
    "dreame.vacuum.r2209":106,
    "dreame.vacuum.p2009":188,
    "dreame.vacuum.r2240":111,
    "dreame.vacuum.r2228o":182,
    "dreame.vacuum.r2492a":470,
    "dreame.vacuum.r2416a":514,
    "mova.vacuum.r2491a":425,
}

def test_v03_has_seven_model_profiles_with_expected_counts():
    doc=json.loads((ROOT/"catalog/models.json").read_text())
    assert len(doc["models"])>=7
    for model_id,count in EXPECTED.items():
        profile=event_profile_for_model(model_id)
        assert profile["known_count"]==count
        assert len(profile["known_event_ids"])==count

def test_only_x10_is_hardware_verified_by_vvh():
    doc=json.loads((ROOT/"catalog/models.json").read_text())
    verified=[m["id"] for m in doc["models"] if m.get("device_tested")]
    assert verified==["dreame.vacuum.r2209"]

def test_aliases_resolve_to_canonical_models():
    assert model_by_id("dreame.vacuum.r2492j")["id"]=="dreame.vacuum.r2492a"
    assert model_by_id("dreame.vacuum.r2416c")["id"]=="dreame.vacuum.r2416a"
    assert model_by_id("dreame.vacuum.r2491")["id"]=="mova.vacuum.r2491a"

def test_every_model_runtime_adapter_resolves():
    for model_id in EXPECTED:
        adapter=get_model(model_id)
        assert callable(adapter.package)
        assert callable(adapter.make_voice_value)

def test_transport_policy_is_fail_closed():
    d9=model_by_id("dreame.vacuum.p2009")
    with pytest.raises(RuntimeError,match="build/coverage-only"):
        _validate_transport(d9,False)

    x40=model_by_id("dreame.vacuum.r2416a")
    with pytest.raises(RuntimeError,match="allow-experimental-transport"):
        _validate_transport(x40,False)
    assert _validate_transport(x40,True)["verification"]=="family-inferred"

    x10=model_by_id("dreame.vacuum.r2209")
    assert _validate_transport(x10,False)["verification"]=="hardware-verified"
