"""v0.20 source-backed research identities and text-only locale expansion."""
import json
from pathlib import Path

import pytest

from vacuum_voice_hub.catalog import model_by_id, models, voices
from vacuum_voice_hub.script_packs import list_locales, script_for_model
from vacuum_voice_hub.model_discovery import summarize_model
from vacuum_voice_hub.install import _validate_transport

ROOT = Path(__file__).resolve().parents[1]
NEW_MODELS = {
    "jdyw.vacuum.u400g", "jdyw.vacuum.t300g", "deerma.vacuum.a2509",
    "narwa.vacuum.ax24", "eco.vacuum.tveglj", "dji.vacuum.romo",
    "homend.vacuum.1293h", "xtl.vacuum.3512",
}


def test_catalog_223_profiles_and_55_attributed_voice_variants():
    data = json.loads((ROOT / "catalog" / "models.json").read_text("utf-8"))
    assert len(models()) == 223
    assert len(voices()) == 55
    assert len({m["id"] for m in models()}) == 223
    assert set(data["expansion"]["added_model_ids_v020"]) == NEW_MODELS
    assert (ROOT / "catalog" / "models.json").read_bytes() == (
        ROOT / "vacuum_voice_hub" / "data" / "models.json").read_bytes()
    for model_id in NEW_MODELS:
        model = model_by_id(model_id)
        assert model["device_tested"] is False
        assert model["adapter"] == "semantic_bundle"
        assert model["transport"]["kind"] == "unsupported-local"
        assert model["transport"]["allow_default"] is False
        assert model["transport"]["evidence"] == data["expansion"]["v020_source"]
        assert summarize_model(model_id)["custom_install_status"] == "build-only"
        with pytest.raises(RuntimeError, match="build/coverage-only"):
            _validate_transport(model, True)
    assert [m["id"] for m in models() if m["device_tested"]] == ["dreame.vacuum.r2209"]


@pytest.mark.parametrize("locale", ["id", "vi", "ar", "hi"])
def test_community_text_templates_are_distinct_from_recorded_audio(locale):
    locales = {r["locale"]: r for r in list_locales()}
    assert len(locales) == 22
    assert locales[locale]["scripted_events"] == 16
    assert locales[locale]["prerecorded"] is False
    result = script_for_model(locale, "deerma.vacuum.a2509")
    assert result["scripted_count"] == 16
    assert result["mapped_count"] > 0
    assert result["status"] == "text-only-not-audio-pack"
    assert result["model_install_authorized"] is False
    assert result["prerecorded"] is False
    assert all(r["text"].strip() and r["translation_source"] == "built-in-text"
               for r in result["entries"])
