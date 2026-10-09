import json
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from vacuum_voice_hub.catalog import model_by_id, models, voices, event_profile_for_model
from vacuum_voice_hub.install import _validate_transport
from vacuum_voice_hub.script_packs import list_locales, script_for_model, synthesize_workspace
from vacuum_voice_hub.creator import validate_workspace

ROOT = Path(__file__).resolve().parents[1]


def test_all_18_locales_are_real_text_templates_not_recorded_voice_claims():
    doc = json.loads((ROOT / "vacuum_voice_hub" / "data" / "script_templates.json").read_text())
    assert doc["schema"] == "vvh.script-pack.v1"
    assert doc["status"] == "text-only-not-audio-pack"
    assert len(doc["locales"]) >= 18
    assert len(doc["semantics"]) == 16
    for code, data in doc["locales"].items():
        assert set(data["phrases"]) == set(doc["semantics"]), code
        assert all(isinstance(x, str) and x.strip() for x in data["phrases"].values())
    listed = list_locales()
    assert len(listed) >= 18
    assert all(v["prerecorded"] is False for v in listed)
    assert len(voices()) == 55  # no fake attributed audio variants


@pytest.mark.parametrize("locale", ["ru", "uk", "de", "fr", "en", "ja", "ko", "zh-Hans"])
def test_script_is_model_aware_and_never_authorizes_install(locale):
    report = script_for_model(locale, "xiaomi.vacuum.d101")
    assert report["locale"] == locale
    assert report["scripted_count"] == 16
    assert report["prerecorded"] is False
    assert report["model_install_authorized"] is False
    assert len(report["entries"]) == 16
    assert report["mapped_count"] > 0
    allowed = set(event_profile_for_model("xiaomi.vacuum.d101")["known_event_ids"])
    assert all(set(row["target_event_ids"]).issubset(allowed)
               for row in report["entries"])


def test_new_models_are_research_only_and_old_identity_registry_unchanged():
    doc = json.loads((ROOT / "catalog" / "models.json").read_text())
    old = json.loads((ROOT / "tests" / "fixtures" / "v08_model_identity.json").read_text())
    assert len(doc["models"]) >= 215
    assert len(voices()) == 55
    assert doc["expansion"]["source_backed_added"] == 45
    for entry in old["models"]:
        assert model_by_id(entry["id"])["id"] == entry["id"]
        for alias in entry["aliases"]:
            assert model_by_id(alias)["id"] == entry["id"]
    for mid in doc["expansion"]["added_model_ids"]:
        model = model_by_id(mid)
        assert model["device_tested"] is False
        assert model["transport"]["kind"] == "unsupported-local"
        assert model["transport"]["allow_default"] is False
        with pytest.raises(RuntimeError, match="build/coverage-only"):
            _validate_transport(model, True)
    assert [m["id"] for m in models() if m.get("device_tested")] == ["dreame.vacuum.r2209"]


def test_synthetic_audio_requires_explicit_user_opt_in(tmp_path):
    with pytest.raises(PermissionError, match="allow-synthetic"):
        synthesize_workspace("ru", "dreame.vacuum.r2209", "sample_pack",
                             "tester", "ru", output=tmp_path / "sample_pack")
    assert not (tmp_path / "sample_pack").exists()


def test_synthetic_workspace_uses_local_engine_and_creator_format(tmp_path, monkeypatch):
    monkeypatch.setattr("vacuum_voice_hub.script_packs.shutil.which", lambda name: "/fake/espeak-ng")
    def fake_tts(cmd, **kwargs):
        output = Path(cmd[cmd.index("-w") + 1])
        output.write_bytes(b"RIFF" + b"test synthetic voice")
        return CompletedProcess(cmd, 0)
    monkeypatch.setattr("vacuum_voice_hub.script_packs.subprocess.run", fake_tts)
    target = tmp_path / "russian_synth"
    result = synthesize_workspace("ru", "dreame.vacuum.r2209",
                                  "russian_synth", "QA test", "ru",
                                  output=target, allow_synthetic=True)
    assert result["audio_files_generated"] is True
    assert result["events_synthesized"] == 16
    assert not result["install_authorized"]
    assert len(list((target / "audio").glob("*.wav"))) == 16
    validation = validate_workspace(target)
    assert validation["ok"], validation["errors"]
    assert validation["valid_events"] == 16
    assert validation["manifest"]["language"] == "ru"
    assert validation["manifest"]["license"] == "UNLICENSED"


def test_synthetic_workspace_does_not_overwrite_existing_path(tmp_path, monkeypatch):
    root = tmp_path / "present"
    root.mkdir()
    monkeypatch.setattr("vacuum_voice_hub.script_packs.shutil.which", lambda name: "/fake/espeak-ng")
    with pytest.raises(FileExistsError):
        synthesize_workspace("uk", "dreame.vacuum.r2209", "present", "QA", "uk",
                             output=root, allow_synthetic=True)
    assert root.is_dir()


def test_cli_locales_and_model_filters_smoke():
    import subprocess, sys
    command = [sys.executable, "-m", "vacuum_voice_hub"]
    result = subprocess.run(command + ["languages"], check=True, capture_output=True, text=True)
    info = json.loads(result.stdout)
    assert len(info["text_only_script_locales"]) >= 18
    assert info["recorded_language_count"] == 7
    result = subprocess.run(command + ["models", "--search", "L40s"],
                            check=True, capture_output=True, text=True)
    assert "dreame.vacuum.r2551a" in result.stdout
    result = subprocess.run(command + ["scripts", "show", "--language", "ru",
                                        "--model", "dreame.vacuum.r2209"],
                            check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["scripted_count"] == 16
