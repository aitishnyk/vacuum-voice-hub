"""v0.20 non-destructive offline audio mastering regression."""
import hashlib
import math
import struct
import subprocess
import sys
import wave

import pytest

from vacuum_voice_hub.audio_mastering import master_preview
from vacuum_voice_hub.audio import ffmpeg_bin


def make_wav(path, amplitude=5000):
    rate = 16000
    signal = ([0] * 4000 +
              [round(amplitude * math.sin(2 * math.pi * 440 * x / rate)) for x in range(rate)] +
              [0] * 4000)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(struct.pack("<" + "h" * len(signal), *signal))


def test_master_preview_trims_normalizes_fades_without_source_modification(tmp_path):
    source = tmp_path / "voice.wav"
    out = tmp_path / "preview" / "master.wav"
    make_wav(source, amplitude=6000)  # Within the guarded +12 dB mastering ceiling.
    checksum = hashlib.sha256(source.read_bytes()).hexdigest()
    result = master_preview(source, out, target_peak_dbfs=-4, padding_ms=50, fade_ms=10)
    assert result["schema"] == "vvh.master-preview.v1"
    assert result["source_sha256"] == checksum
    assert result["output_sha256"] == hashlib.sha256(out.read_bytes()).hexdigest()
    assert result["removed_leading_frames"] > 0
    assert result["removed_trailing_frames"] > 0
    assert result["after"]["sample_rate"] == 16000
    assert result["after"]["duration_sec"] < result["before"]["signal"]["duration_sec"]
    assert -5.0 < result["after"]["peak_dbfs"] < -3.9
    assert result["creator_manifest_changed"] is False
    assert result["human_review_required"] is True
    assert result["install_authorized"] is False
    assert result["redistribution_verified"] is False
    assert hashlib.sha256(source.read_bytes()).hexdigest() == checksum
    with pytest.raises(FileExistsError):
        master_preview(source, out)


@pytest.mark.parametrize("bad,kw", [
    ("target_peak_dbfs", 0),
    ("target_peak_dbfs", -19),
    ("target_peak_dbfs", float("nan")),
    ("silence_dbfs", -80),
    ("padding_ms", -1),
    ("fade_ms", 250),
    ("fade_ms", float("inf")),
    ("trim_silence", 1),
])
def test_invalid_master_parameters_do_not_leave_outputs(tmp_path, bad, kw):
    source = tmp_path / "voice.wav"
    make_wav(source)
    out = tmp_path / "result.wav"
    with pytest.raises(ValueError):
        master_preview(source, out, **{bad: kw})
    assert not out.exists()


def test_refuse_silence_or_too_quiet_material(tmp_path):
    src = tmp_path / "silent.wav"
    make_wav(src, amplitude=0)
    with pytest.raises(ValueError, match="no audio above"):
        master_preview(src, tmp_path / "silent-out.wav")
    assert not (tmp_path / "silent-out.wav").exists()
    make_wav(src, amplitude=100)
    with pytest.raises(ValueError, match="too quiet"):
        master_preview(src, tmp_path / "quiet-out.wav", silence_dbfs=-70)
    assert not (tmp_path / "quiet-out.wav").exists()


def test_mastering_rejects_same_source_and_existing_symlink(tmp_path):
    source = tmp_path / "voice.wav"
    make_wav(source)
    with pytest.raises(ValueError, match="different"):
        master_preview(source, source)
    target = tmp_path / "link.wav"
    target.symlink_to(source)
    with pytest.raises((ValueError, FileExistsError)):
        master_preview(source, target)
    assert target.is_symlink()


def test_compressed_mp3_mastering_and_cli(tmp_path):
    src = tmp_path / "voice.wav"
    mp3 = tmp_path / "voice.mp3"
    make_wav(src)
    subprocess.run([ffmpeg_bin(), "-nostdin", "-hide_banner", "-loglevel", "error",
                    "-i", str(src), "-c:a", "libmp3lame", str(mp3)],
                   capture_output=True, check=True, timeout=30)
    dest = tmp_path / "compressed-master.wav"
    report = master_preview(mp3, dest, trim_silence=False, target_peak_dbfs=-6)
    assert report["source_format"] == ".mp3"
    assert report["removed_leading_frames"] == 0
    cli = subprocess.run([sys.executable, "-m", "vacuum_voice_hub", "creator",
                          "master-preview", "--help"],
                         capture_output=True, text=True, check=True)
    assert "--target-peak-dbfs" in cli.stdout
