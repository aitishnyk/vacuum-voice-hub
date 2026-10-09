import json
import subprocess
import sys
from pathlib import Path

import pytest

from vacuum_voice_hub.script_packs import script_for_model
from vacuum_voice_hub.translation_overlays import load_overlay, translation_scaffold
from vacuum_voice_hub.catalog import event_profile_for_model

ROOT = Path(__file__).resolve().parents[1]
MODEL = "dreame.vacuum.r2209"


def _write(tmp_path, translations=None, **overrides):
    record = {
        "schema": "vvh.translation-overlay.v1",
        "locale": "uk",
        "author": "Local translator",
        "license": "UNLICENSED",
        "source_url": None,
        "translations": translations or {"error.bumper": "Перевірте бампер робота."},
    }
    record.update(overrides)
    path = tmp_path / "overlay.json"
    path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    return path


def test_translation_scaffold_has_reference_only_and_does_not_fake_audio():
    candidate = translation_scaffold("uk", MODEL, 512)
    assert candidate["schema"] == "vvh.translation-overlay.v1"
    assert candidate["locale"] == "uk"
    assert candidate["translations"] == {}
    assert candidate["candidate_count"] > 0
    assert candidate["core_script_count"] == 16
    assert not candidate["install_authorized"]
    assert not candidate["audio_files_generated"]
    allowed = set(event_profile_for_model(MODEL)["known_event_ids"])
    for entry in candidate["translation_candidates"]:
        assert set(entry["target_event_ids"]).issubset(allowed)
        assert entry["english_reference_not_translated"]


def test_overlay_extends_core_scripts_and_credits_user_translation(tmp_path):
    path = _write(tmp_path, {"error.bumper": "Перевірте бампер робота.",
                             "clean.start": "Починаю прибирання."})
    loaded = load_overlay(path, "uk")
    assert loaded["reviewed"] is False
    assert not loaded["audio_files_generated"]
    report = script_for_model("uk", MODEL, overlay_path=path)
    assert report["scripted_count"] == 17
    assert report["overlay_count"] == 2
    assert report["overlay_attribution"]["author"] == "Local translator"
    assert not report["model_install_authorized"]
    assert report["model_event_count"] >= report["mapped_event_count"]
    assert report["model_event_coverage_pct"] >= script_for_model("uk", MODEL)["model_event_coverage_pct"]
    row = next(e for e in report["entries"] if e["semantic"] == "error.bumper")
    assert row["translation_source"] == "user-overlay"
    assert row["text"] == "Перевірте бампер робота."


@pytest.mark.parametrize("problem,pattern", [
    ({"locale": "ru"}, "locale"),
    ({"author": ""}, "author"),
    ({"license": ""}, "license"),
    ({"source_url": "http://example.com"}, "HTTPS"),
    ({"translations": {"fictional.action": "Привіт"}}, "unknown semantic"),
    ({"translations": {"error.bumper": ""}}, "invalid translated"),
    ({"translations": {"error.bumper": "A" * 401}}, "invalid translated"),
    ({"translations": {"error.bumper": "Line 1\nLine 2"}}, "invalid translated"),
])
def test_bad_translation_overlays_fail_closed(tmp_path, problem, pattern):
    path = _write(tmp_path, **problem)
    with pytest.raises(ValueError, match=pattern):
        load_overlay(path, "uk")


def test_overlay_duplicate_json_keys_refused(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"schema":"vvh.translation-overlay.v1","locale":"uk",'
                    '"author":"test","license":"UNLICENSED","translations":{'
                    '"error.bumper":"A","error.bumper":"B"}}')
    with pytest.raises(ValueError, match="duplicate"):
        load_overlay(path, "uk")


def test_large_translation_overlay_refused(tmp_path):
    path = tmp_path / "huge.json"
    path.write_bytes(b" " * (128 * 1024 + 1))
    with pytest.raises(ValueError, match="exceeds"):
        load_overlay(path, "uk")


def test_cli_scaffold_and_audit_without_network_or_robot(tmp_path):
    base = [sys.executable, "-m", "vacuum_voice_hub", "scripts"]
    path = tmp_path / "template.json"
    out = subprocess.run(base + ["scaffold", "--language", "uk", "--model", MODEL,
                                "--output", str(path)], check=True, capture_output=True, text=True)
    result = json.loads(out.stdout)
    assert result["candidate_count"] > 0
    assert path.is_file()
    assert json.loads(path.read_text())["translations"] == {}
    second = subprocess.run(base + ["scaffold", "--language", "uk", "--model", MODEL,
                                    "--output", str(path)], capture_output=True, text=True)
    assert second.returncode != 0  # refuses overwriting user-made translation files
    overlay = _write(tmp_path)
    audit = subprocess.run(base + ["audit", "--language", "uk", "--model", MODEL,
                                   "--overlay", str(overlay)], check=True, capture_output=True, text=True)
    result = json.loads(audit.stdout)
    assert result["overlay_count"] == 1
    assert result["model_install_authorized"] is False
    assert result["model_event_count"] >= result["mapped_event_count"]


def test_legacy_18_text_locales_and_154_model_catalog_unchanged():
    original = script_for_model("uk", MODEL)
    assert original["scripted_count"] == 16
    assert original["overlay_count"] == 0
    assert original["overlay_attribution"] is None
    from vacuum_voice_hub.catalog import models, voices
    assert len(models()) == 154
    assert len(voices()) == 55


def test_user_translation_overlay_generates_extra_piper_audio(tmp_path, monkeypatch):
    import wave
    from vacuum_voice_hub.piper_studio import synthesize_piper_workspace
    voice = tmp_path / "voice.onnx"
    voice.write_bytes(b"LOCAL MODEL")
    (tmp_path / "voice.onnx.json").write_text(json.dumps({"language":{"code":"uk_UA"}}))
    overlay = _write(tmp_path)
    monkeypatch.setattr("vacuum_voice_hub.piper_studio.shutil.which", lambda name: "/local/piper")
    calls = []
    def fake_piper(cmd, *, input, text, capture_output, check, timeout):
        calls.append(input)
        dest = Path(cmd[cmd.index("--output_file")+1])
        with wave.open(str(dest), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(16000)
            out.writeframes(b"\x00\x20" * 16000)
        return subprocess.CompletedProcess(cmd, 0)
    monkeypatch.setattr("vacuum_voice_hub.piper_studio.subprocess.run", fake_piper)
    report = synthesize_piper_workspace("uk", MODEL, "extended_uk", "Translator",
                                        voice, output=tmp_path/"extended_uk",
                                        allow_synthetic=True, overlay_path=overlay)
    assert report["events_synthesized"] == 17
    assert report["overlay_count"] == 1
    assert len(calls) == 17
    assert (tmp_path/"extended_uk"/"audio"/"error.bumper.wav").is_file()
    assert report["install_authorized"] is False
