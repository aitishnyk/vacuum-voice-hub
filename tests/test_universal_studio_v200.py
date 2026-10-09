"""v2.0 integrated Studio API and source-stable truth constraints."""
import hashlib
import json
import subprocess
import sys
import wave
import pytest

from vacuum_voice_hub.creator import new_workspace, assign_audio
from vacuum_voice_hub.universal_studio import (
    studio_capabilities, inspect_studio, export_studio_report
)


def project(tmp_path):
    root = tmp_path / "owned-voice"
    new_workspace(root, pack_id="owned_voice", name="Owner source",
                  author="Contributor", language="uk",
                  license_name="UNLICENSED")
    sound = tmp_path / "clip.wav"
    with wave.open(str(sound), "wb") as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(16000)
        wav.writeframes(b"\x00\x20" * 16000)
    for semantic in ("clean.start","clean.pause"):
        assign_audio(root, semantic, sound)
    return root


def test_capabilities_keep_223_55_22_truth():
    report = studio_capabilities()
    assert report["model_profiles"] >= 223
    assert report["recorded_voice_variants"] == 55
    assert report["text_script_locales"] >= 22
    assert report["physically_verified_models"] >= 1
    assert report["model_profiles_are_physical_installs"] is False
    assert report["text_locales_are_recordings"] is False
    assert report["hardware_install_authorized"] is False


def test_integrated_report_keeps_rights_and_hardware_separate(tmp_path):
    root = project(tmp_path)
    initial = (root / "manifest.json").read_bytes()
    result = inspect_studio(root, "dreame.vacuum.r2209", "uk")
    assert result["schema"] == "vvh.universal-studio.v1"
    assert result["pack_id"] == "owned_voice"
    assert result["workspace_valid"]
    assert result["declared_license"] == "UNLICENSED"
    assert result["source_manifest_sha256"] == hashlib.sha256(initial).hexdigest()
    assert result["assigned_audio_semantics"] == 2
    assert result["model_known_events"] >= result["model_mapped_events"] >= 2
    assert result["workspace_language_matches_script"]
    assert result["hardware_install_authorized"] is False
    assert result["redistribution_rights_verified"] is False
    assert result["independent_human_language_verified"] is False
    assert (root / "manifest.json").read_bytes() == initial
    assert str(tmp_path) not in json.dumps(result)


def test_invalid_workspace_fails_closed_without_hardware_claim(tmp_path):
    root = tmp_path / "new-project"
    new_workspace(root, pack_id="empty_test", name="Empty",
                  author="Author", language="en")
    result = inspect_studio(root, "dreame.vacuum.r2209", "en")
    assert not result["workspace_valid"]
    assert not result["offline_pack_build_ready"]
    assert not result["hardware_install_authorized"]


def test_report_export_new_only_and_cli_round_trip(tmp_path):
    root = project(tmp_path)
    dest = tmp_path / "studio-report.json"
    exported = export_studio_report(root, "dreame.vacuum.r2209", "uk", dest)
    assert exported["report_sha256"] == hashlib.sha256(dest.read_bytes()).hexdigest()
    assert not exported["hardware_install_authorized"]
    with pytest.raises(FileExistsError):
        export_studio_report(root, "dreame.vacuum.r2209", "uk", dest)
    cli = [sys.executable, "-m", "vacuum_voice_hub", "studio"]
    def run(*args):
        return json.loads(subprocess.run(cli + list(args), capture_output=True,
                                         text=True, check=True).stdout)
    assert run("capabilities")["model_profiles"] >= 223
    data = run("inspect", "--workspace", str(root), "--model",
               "dreame.vacuum.r2209", "--language", "uk")
    assert data["pack_id"] == "owned_voice"
    assert data["hardware_install_authorized"] is False


def test_optional_translation_review_and_custom_adapter_are_integrated(tmp_path):
    from vacuum_voice_hub.language_review import create_language_review
    root = project(tmp_path)
    translator = tmp_path / "translator.json"
    create_language_review("uk", "dreame.vacuum.r2209", translator)
    adapter = tmp_path / "adapter.json"
    adapter.write_text(json.dumps({
        "schema": "vvh.adapter-descriptor.v1",
        "adapter_id": "community-audio",
        "model_id": "dreame.vacuum.r2209",
        "author": "Contributor", "license": "UNLICENSED",
        "entries": [{"semantic": "clean.start", "archive_name": "start.wav"}]
    }))
    full = inspect_studio(root, "dreame.vacuum.r2209", "uk",
                          adapter_path=adapter, translation_review=translator)
    assert full["adapter"]["ready_for_offline_interchange"]
    assert full["adapter"]["mapped_events"] == 1
    assert full["translation_review"]["claimed_human_approvals"] == 0
    assert not full["adapter"]["hardware_install_authorized"]
    assert not full["redistribution_rights_verified"]
    with pytest.raises(ValueError, match="mismatch"):
        inspect_studio(root, "dreame.vacuum.r2209", "en",
                       translation_review=translator)


def test_wrong_locale_and_unknown_model_do_not_authorize(tmp_path):
    root = project(tmp_path)
    with pytest.raises((KeyError, ValueError)):
        inspect_studio(root, "not.an.actual.model", "uk")
    with pytest.raises((KeyError, ValueError)):
        inspect_studio(root, "dreame.vacuum.r2209", "zz-INVALID-FAKE")
