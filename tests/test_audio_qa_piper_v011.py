"""Read-only signal QA and offline Piper integration regressions."""
import json
import math
import struct
import subprocess
import sys
import wave
from pathlib import Path

import pytest

from vacuum_voice_hub.audio_qa import inspect_wav, inspect_workspace
from vacuum_voice_hub.creator import new_workspace, assign_audio
from vacuum_voice_hub.piper_studio import synthesize_piper_workspace


def _wav(path, *, seconds=1.0, volume=3000, frequency=440, rate=16000):
    values = [int(volume * math.sin(2 * math.pi * frequency * i / rate))
              for i in range(int(rate * seconds))]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack("<" + "h" * len(values), *values))


def _voice(tmp_path, code="ru_RU"):
    model = tmp_path / "voice.onnx"
    model.write_bytes(b"LOCAL TEST MODEL ONLY")
    (tmp_path / "voice.onnx.json").write_text(json.dumps({"language": {"code": code}}))
    return model


def test_audio_qa_good_wav_reports_engineering_metrics(tmp_path):
    path = tmp_path / "voice.wav"
    _wav(path)
    result = inspect_wav(path)
    assert result["schema"] == "vvh.wav-audio-qa.v1"
    assert result["sample_rate"] == 16000
    assert result["channels"] == 1
    assert result["duration_sec"] == 1.0
    assert result["pass_basic_checks"] is True
    assert result["clipped_pct"] == 0
    assert result["install_authorized"] if "install_authorized" in result else True


@pytest.mark.parametrize("volume,warning", [
    (0, "very-quiet"),
    (32767, "clipping"),
])
def test_audio_qa_warning_detection(tmp_path, volume, warning):
    path = tmp_path / "voice.wav"
    _wav(path, volume=volume)
    result = inspect_wav(path)
    assert warning in result["warnings"]
    assert result["pass_basic_checks"] is False


def test_audio_qa_truncated_or_non_wav_is_rejected(tmp_path):
    path = tmp_path / "invalid.wav"
    path.write_bytes(b"not a valid wav file")
    with pytest.raises(ValueError, match="invalid WAV"):
        inspect_wav(path)


def test_workspace_audio_qa_preserves_files_and_reports_coverage(tmp_path):
    root = tmp_path / "voice_project"
    new_workspace(root, pack_id="voice_project", name="Voice", author="QA", language="ru")
    wav = tmp_path / "source.wav"
    _wav(wav)
    assign_audio(root, "clean.start", wav)
    before = (root / "manifest.json").read_bytes()
    result = inspect_workspace(root, model_id="dreame.vacuum.r2209")
    assert result["ok"] is True
    assert result["analyzed_wav"] == 1
    assert result["coverage"]["model_id"] == "dreame.vacuum.r2209"
    assert not result["install_authorized"]
    assert (root / "manifest.json").read_bytes() == before


def test_piper_requires_explicit_opt_in_before_synthesis(tmp_path):
    target = tmp_path / "target"
    with pytest.raises(PermissionError):
        synthesize_piper_workspace("ru", "dreame.vacuum.r2209", "target", "Author",
                                   tmp_path / "missing.onnx", output=target)
    assert not target.exists()


def test_piper_needs_matching_local_config_and_language(tmp_path):
    target = tmp_path / "target"
    model = _voice(tmp_path, code="en_US")
    with pytest.raises(ValueError, match="language"):
        synthesize_piper_workspace("ru", "dreame.vacuum.r2209", "target", "Author",
                                   model, output=target, allow_synthetic=True)
    assert not target.exists()
    (tmp_path / "voice.onnx.json").unlink()
    with pytest.raises(ValueError, match="configuration"):
        synthesize_piper_workspace("ru", "dreame.vacuum.r2209", "target", "Author",
                                   model, output=target, allow_synthetic=True)


def test_piper_generates_valid_local_wavs_without_network_or_robot(tmp_path, monkeypatch):
    voice = _voice(tmp_path)
    target = tmp_path / "synth"
    monkeypatch.setattr("vacuum_voice_hub.piper_studio.shutil.which",
                        lambda name: "/fake/piper" if name == "piper" else None)
    commands = []
    def fake_run(cmd, *, input, text, capture_output, check, timeout):
        commands.append((cmd, input))
        assert cmd[0] == "/fake/piper"
        assert "--model" in cmd and "--config" in cmd
        assert input.strip()
        _wav(Path(cmd[cmd.index("--output_file") + 1]))
        return subprocess.CompletedProcess(cmd, 0)
    monkeypatch.setattr("vacuum_voice_hub.piper_studio.subprocess.run", fake_run)
    report = synthesize_piper_workspace("ru", "dreame.vacuum.r2209", "piper_ru", "Author",
                                        voice, output=target, speaker=0, allow_synthetic=True)
    assert report["events_synthesized"] == 16
    assert report["audio_files_generated"] is True
    assert report["license_review_required"] is True
    assert report["redistribution_verified"] is False
    assert not report["install_authorized"]
    assert len(commands) == 16
    assert all(cmd[0].count("--speaker") == 1 for cmd in commands)
    inspection = inspect_workspace(target, model_id="dreame.vacuum.r2209")
    assert inspection["analyzed_wav"] == 16
    assert inspection["ok"] is True


def test_piper_failed_partial_synthesis_cleans_only_own_workspace(tmp_path, monkeypatch):
    voice = _voice(tmp_path)
    target = tmp_path / "failed"
    unrelated = tmp_path / "other.txt"
    unrelated.write_text("KEEP")
    monkeypatch.setattr("vacuum_voice_hub.piper_studio.shutil.which", lambda name: "/fake/piper")
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0])
    monkeypatch.setattr("vacuum_voice_hub.piper_studio.subprocess.run", fail)
    with pytest.raises(RuntimeError, match="Piper failed"):
        synthesize_piper_workspace("ru", "dreame.vacuum.r2209", "failed", "Author",
                                   voice, output=target, allow_synthetic=True)
    assert not target.exists()
    assert unrelated.read_text() == "KEEP"


def test_cli_commands_exist_and_do_not_install(tmp_path):
    base = [sys.executable, "-m", "vacuum_voice_hub"]
    result = subprocess.run(base + ["scripts", "piper", "--help"], capture_output=True,
                            text=True, check=True)
    assert "--allow-synthetic" in result.stdout
    result = subprocess.run(base + ["creator", "qa", "--help"], capture_output=True,
                            text=True, check=True)
    assert "--model" in result.stdout
