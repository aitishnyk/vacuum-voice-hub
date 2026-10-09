"""v0.15 actual FFmpeg compressed audio, gain preview and language/audio coverage."""
import hashlib
import json
import math
import struct
import subprocess
import sys
import wave
from pathlib import Path

import pytest

from vacuum_voice_hub.audio import ffmpeg_bin
from vacuum_voice_hub.audio_advanced import inspect_audio, preview_gain
from vacuum_voice_hub.audio_qa import inspect_workspace
from vacuum_voice_hub.creator import assign_audio, new_workspace
from vacuum_voice_hub.creator_batch import preflight_workspace
from vacuum_voice_hub.language_audio_coverage import language_audio_coverage


def make_wav(path, gain=4000, rate=16000):
    samples = [int(gain * math.sin(2 * math.pi * 440 * i / rate)) for i in range(rate)]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack("<" + "h" * len(samples), *samples))


def convert(src, dst, codec):
    subprocess.run([ffmpeg_bin(), "-nostdin", "-hide_banner", "-loglevel", "error",
                    "-i", str(src), "-c:a", codec, "-y", str(dst)],
                   check=True, capture_output=True, timeout=30)


@pytest.fixture
def audio_files(tmp_path):
    src = tmp_path / "original.wav"
    make_wav(src)
    ogg = tmp_path / "voice.ogg"
    mp3 = tmp_path / "voice.mp3"
    convert(src, ogg, "libvorbis")
    convert(src, mp3, "libmp3lame")
    return src, ogg, mp3


@pytest.mark.parametrize("idx", [0, 1, 2])
def test_actual_local_audio_decode_supported_formats(audio_files, idx):
    info = inspect_audio(audio_files[idx])
    assert info["schema"] == "vvh.audio-source-qa.v1"
    assert info["source_format"] in {".wav", ".ogg", ".mp3"}
    assert info["pass_basic_checks"]
    assert not info["decoded_duration_capped"]
    assert not info["install_authorized"]
    assert info["signal"]["duration_sec"] == pytest.approx(1.0, abs=.04)
    assert info["signal"]["rms_dbfs"] < 0


def test_invalid_audio_rejected_without_network(tmp_path):
    bad = tmp_path / "bad.ogg"
    bad.write_bytes(b"not an audio stream")
    with pytest.raises(ValueError, match="could not decode"):
        inspect_audio(bad)
    with pytest.raises(ValueError, match="unsupported"):
        inspect_audio(tmp_path / "bad.json")


def test_unsupported_or_oversized_source_fails_early(tmp_path):
    src = tmp_path / "oversized.ogg"
    with src.open("wb") as w:
        w.truncate(25 * 1024 * 1024 + 1)
    with pytest.raises(ValueError, match="25 MiB"):
        inspect_audio(src)


def test_ffmpeg_decode_timeout_is_bounded_and_fails(tmp_path, monkeypatch):
    import vacuum_voice_hub.audio_advanced as module
    src = tmp_path / "in.ogg"
    src.write_bytes(b"data")
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], timeout=45)
    monkeypatch.setattr(module.subprocess, "run", timeout)
    with pytest.raises(ValueError, match="timed out"):
        module.inspect_audio(src)


def test_creator_workspace_compressed_source_requires_opt_in(audio_files, tmp_path):
    root = tmp_path / "project"
    new_workspace(root, pack_id="project", name="Project", author="QA",
                  language="ru", license_name="UNLICENSED")
    assign_audio(root, "clean.start", audio_files[1])
    before = (root / "manifest.json").read_bytes()
    skipped = inspect_workspace(root, decode_compressed=False)
    assert skipped["unanalysed_formats"] == 1
    assert skipped["analyzed_wav"] == 0
    report = inspect_workspace(root, decode_compressed=True)
    assert report["unanalysed_formats"] == 0
    assert report["decoded_compressed"] == 1
    assert report["audio"][0]["source_format"] == ".ogg"
    assert report["ok"]
    assert (root / "manifest.json").read_bytes() == before
    preflight = preflight_workspace(root, "dreame.vacuum.r2209", check_audio=True)
    assert preflight["audio_warnings"][0]["warnings"] == ["not-analyzed"]
    checked = preflight_workspace(root, "dreame.vacuum.r2209",
                                  check_audio=True, decode_compressed=True)
    assert not checked["audio_warnings"]


def test_gain_preview_is_non_destructive_and_provides_relative_metrics(audio_files, tmp_path):
    src = audio_files[0]
    before = hashlib.sha256(src.read_bytes()).hexdigest()
    output = tmp_path / "previews" / "minus-six.wav"
    result = preview_gain(src, output, -6)
    assert result["schema"] == "vvh.gain-preview.v1"
    assert result["gain_db"] == -6
    assert result["bytes"] == output.stat().st_size
    assert result["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert result["creator_manifest_changed"] is False
    assert result["install_authorized"] is False
    assert result["redistribution_verified"] is False
    assert result["after"]["signal"]["rms_dbfs"] < result["before"]["signal"]["rms_dbfs"]
    assert hashlib.sha256(src.read_bytes()).hexdigest() == before
    with pytest.raises(FileExistsError):
        preview_gain(src, output, 0)
    with pytest.raises(ValueError, match="different"):
        preview_gain(src, src, 0)
    with pytest.raises(ValueError, match="-12"):
        preview_gain(src, tmp_path / "bad.wav", 13)
    assert not (tmp_path / "bad.wav").exists()


def test_locale_coverage_distinguishes_text_from_actual_audio(audio_files, tmp_path):
    root = tmp_path / "language"
    new_workspace(root, pack_id="language", name="Language", author="QA",
                  language="uk", license_name="UNLICENSED")
    assign_audio(root, "clean.start", audio_files[0])
    report = language_audio_coverage(root, "uk", "dreame.vacuum.r2209")
    assert report["schema"] == "vvh.language-audio-coverage.v1"
    assert report["ok"]
    assert report["workspace_language_matches_script"] is True
    assert report["scripted_event_count"] >= 1
    assert report["text_model_event_count"] >= 1
    assert report["audio_assigned_model_event_count"] >= 1
    assert report["declared_locale_text_and_audio_event_count"] >= 1
    assert report["audio_coverage_pct"] < report["text_coverage_pct"]
    assert "clean.start" not in report["missing_audio_semantics"]
    assert not report["speaker_language_verified"]
    assert not report["recording_license_verified"]
    mismatch = language_audio_coverage(root, "ru", "dreame.vacuum.r2209")
    assert mismatch["workspace_language_matches_script"] is False
    assert mismatch["audio_coverage_pct"] == 0
    assert mismatch["audio_assigned_model_event_count"] >= 1
    assert not mismatch["install_authorized"]


def test_language_coverage_with_user_translated_additions(audio_files, tmp_path):
    root = tmp_path / "extra"
    new_workspace(root, pack_id="extra", name="Extra", author="QA",
                  language="uk", license_name="UNLICENSED")
    assign_audio(root, "error.bumper", audio_files[0])
    overlay = tmp_path / "custom.json"
    overlay.write_text(json.dumps({
        "schema": "vvh.translation-overlay.v1", "locale": "uk",
        "author": "Translator", "license": "UNLICENSED",
        "translations": {"error.bumper": "Перевірте бампер робота."}
    }, ensure_ascii=False))
    basic = language_audio_coverage(root, "uk", "dreame.vacuum.r2209")
    extended = language_audio_coverage(root, "uk", "dreame.vacuum.r2209",
                                       overlay_path=overlay)
    assert extended["overlay_count"] == 1
    assert extended["audio_assigned_in_script"] >= basic["audio_assigned_in_script"]
    assert extended["install_authorized"] is False


def test_cli_new_commands_exist(tmp_path):
    base = [sys.executable, "-m", "vacuum_voice_hub", "creator"]
    for name in ("gain-preview", "language-coverage"):
        result = subprocess.run(base + [name, "--help"],
                                check=True, capture_output=True, text=True)
        assert "usage:" in result.stdout
    result = subprocess.run(base + ["qa", "--help"],
                            check=True, capture_output=True, text=True)
    assert "--decode-compressed" in result.stdout
