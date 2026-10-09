"""V0.13 multi-brand identity expansion, preservation and conservative comparison."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from vacuum_voice_hub.catalog import models, model_by_id, voices
from vacuum_voice_hub.install import _validate_transport
from vacuum_voice_hub.model_discovery import summarize_model, compare_models

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "catalog" / "models.json"
MIRROR = ROOT / "vacuum_voice_hub" / "data" / "models.json"


def test_all_154_previous_profiles_preserve_alias_adapter_transport():
    previous = json.loads((ROOT / "tests" / "fixtures" / "v012_model_identity.json").read_text())
    assert previous["count"] == 154
    for entry in previous["models"]:
        m = model_by_id(entry["id"])
        assert m["id"] == entry["id"]
        assert m["adapter"] == entry["adapter"]
        assert m["transport"]["kind"] == entry["transport"]
        assert m["device_tested"] == entry["device_tested"]
        for alias in entry["aliases"]:
            assert model_by_id(alias)["id"] == entry["id"]


def test_new_61_source_attributed_profile_ids_are_fail_closed():
    doc = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert len(doc["models"]) == 215
    assert len(voices()) == 55
    assert doc["expansion"]["previous_count"] == 154
    added = doc["expansion"]["added_model_ids_v013"]
    assert len(added) == len(set(added)) == 61
    origins = doc["expansion"]["source_by_family"]
    for id_ in added:
        m = model_by_id(id_)
        brand = id_.split(".")[0]
        assert brand in origins
        assert m["transport"]["evidence"] == origins[brand]
        assert m["catalog_source"].startswith("Public MIoT")
        assert m["device_tested"] is False
        assert m["adapter"] == "semantic_bundle"
        assert m["event_profile"] == "semantic-portable-core-v1"
        assert m["transport"]["kind"] == "unsupported-local"
        assert m["transport"]["verification"] == "build-only"
        assert not m["transport"]["allow_default"]
        assert m.get("product_id") is None and m.get("plugin_id") is None
        with pytest.raises(RuntimeError, match="build/coverage-only"):
            _validate_transport(m, True)


def test_catalog_mirror_exact_and_no_alias_collisions():
    assert SOURCE.read_bytes() == MIRROR.read_bytes()
    mm = models()
    ids = [m["id"] for m in mm]
    assert len(ids) == len(set(ids)) == 215
    aliases = {}
    for m in mm:
        for name in m["aliases"]:
            assert name not in aliases or aliases[name] == m["id"]
            aliases[name] = m["id"]
            assert model_by_id(name)["id"] == m["id"]
    assert [m["id"] for m in mm if m["device_tested"]] == ["dreame.vacuum.r2209"]


@pytest.mark.parametrize("id_,brand", [
    ("viomi.vacuum.v60", "viomi"),
    ("xiaomi.vacuum.d109gl", "xiaomi"),
    ("roborock.vacuum.a75", "roborock"),
    ("roidmi.vacuum.v63", "roidmi"),
    ("ijai.vacuum.v17", "ijai"),
])
def test_discovery_covers_five_brands_without_install_claim(id_, brand):
    info = summarize_model(id_)
    assert info["id"].startswith(brand + ".")
    assert info["custom_install_status"] == "build-only"
    assert info["install_default"] is False
    assert info["transport_source"].startswith("https://home.miot-spec.com/")


def test_model_comparison_does_not_transfer_hardware_verification():
    report = compare_models("dreame.vacuum.r2209", "roborock.vacuum.a75")
    assert report["schema"] == "vvh.model-comparison.v1"
    assert report["common_event_count"] >= 5
    assert report["left"]["device_tested"] is True
    assert report["right"]["device_tested"] is False
    assert not report["custom_install_compatibility_proved"]
    assert not report["install_authorized_by_comparison"]
    assert report["right"]["custom_install_status"] == "build-only"


def test_comparison_of_identical_model_has_100pct_event_overlap_but_no_install():
    report = compare_models("viomi.vacuum.v60", "viomi.vacuum.v60")
    assert report["event_overlap_left_pct"] == 100
    assert report["event_overlap_right_pct"] == 100
    assert not report["install_authorized_by_comparison"]


def test_cli_compare_output_and_failure_for_unknown_model():
    base = [sys.executable, "-m", "vacuum_voice_hub", "model-compare"]
    result = subprocess.run(base + ["roborock.vacuum.a75", "viomi.vacuum.v60"],
                            check=True, capture_output=True, text=True)
    info = json.loads(result.stdout)
    assert info["left"]["id"] == "roborock.vacuum.a75"
    assert info["right"]["id"] == "viomi.vacuum.v60"
    assert info["same_build_adapter"] is True
    assert info["install_authorized_by_comparison"] is False
    bad = subprocess.run(base + ["no.such.model", "viomi.vacuum.v60"],
                         capture_output=True, text=True)
    assert bad.returncode != 0


def test_new_xiaomi_and_roborock_are_not_misclassified_as_legacy_installer():
    for ident in ("xiaomi.vacuum.ov51gl", "xiaomi.vacuum.ov42gl",
                  "roborock.vacuum.a73", "roidmi.vacuum.sdj60"):
        model = model_by_id(ident)
        assert model["adapter"] == "semantic_bundle"
        assert model["transport"]["kind"] == "unsupported-local"
