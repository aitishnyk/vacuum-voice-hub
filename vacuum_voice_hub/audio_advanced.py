"""Bounded, offline audio-source decoding and non-destructive gain preview.

The audio's exact language, speaker rights and robot playback are not verified.
Do not treat these engineering checks as install permission.
"""
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .audio import ffmpeg_bin
from .audio_qa import MAX_AUDIO_BYTES, MAX_DURATION_SEC, inspect_wav

SOURCE_SUFFIXES = frozenset({".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac", ".opus"})
MAX_PCM_BYTES = 6_500_000  # mono 16 kHz, 181 seconds plus WAV overhead
MAX_FFMPEG_SECONDS = 45


def _source(path):
    src = Path(path).expanduser().resolve(strict=True)
    if not src.is_file() or src.suffix.lower() not in SOURCE_SUFFIXES:
        raise ValueError("unsupported audio input type")
    size = src.stat().st_size
    if not 0 < size <= MAX_AUDIO_BYTES:
        raise ValueError("audio source must be 1 byte..25 MiB")
    return src


def _decode(src, output, gain_db=None):
    """Produce bounded mono PCM using local FFmpeg, with no network protocols."""
    cmd = [ffmpeg_bin(), "-nostdin", "-hide_banner", "-loglevel", "error",
           "-threads", "1", "-protocol_whitelist", "file,pipe",
           "-i", str(src), "-map", "0:a:0", "-vn", "-t", "181",
           "-ac", "1", "-ar", "16000"]
    if gain_db is not None:
        cmd += ["-af", f"volume={gain_db:+.2f}dB"]
    cmd += ["-c:a", "pcm_s16le", "-fs", str(MAX_PCM_BYTES),
            "-f", "wav", "-y", str(output)]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=MAX_FFMPEG_SECONDS,
                                check=False)
    except subprocess.TimeoutExpired as exc:
        raise ValueError("FFmpeg decode timed out") from exc
    if result.returncode:
        raise ValueError("FFmpeg could not decode this local audio source")
    if not output.is_file() or not 44 <= output.stat().st_size <= MAX_PCM_BYTES:
        raise ValueError("decoded audio missing or exceeds safe output bound")


def _metrics(decoded, source_format):
    details = inspect_wav(decoded)
    warnings = list(details["warnings"])
    capped = details["duration_sec"] >= MAX_DURATION_SEC
    if capped and "duration-cap-reached" not in warnings:
        warnings.append("duration-cap-reached")
    return {
        "schema": "vvh.audio-source-qa.v1",
        "source_format": source_format, "signal": details,
        "warnings": warnings, "pass_basic_checks": not warnings,
        "decoded_duration_capped": capped,
        "language_verified": False, "install_authorized": False,
    }


def inspect_audio(path):
    """Inspect WAV directly or decode a bounded compressed source into temporary PCM."""
    src = _source(path)
    if src.suffix.lower() == ".wav":
        return _metrics(src, ".wav")
    with tempfile.TemporaryDirectory(prefix="vvh-source-qa-") as work:
        output = Path(work) / "decoded.wav"
        _decode(src, output)
        return _metrics(output, src.suffix.lower())


def preview_gain(path, output, gain_db):
    """Export NEW PCM WAV at explicit gain; never alter input or Creator manifest."""
    if isinstance(gain_db, bool) or not isinstance(gain_db, (int, float)):
        raise ValueError("gain must be a number in -12..12 dB")
    gain_db = float(gain_db)
    if not -12 <= gain_db <= 12:
        raise ValueError("gain must be in -12..12 dB")
    src = _source(path)
    dest = Path(output).expanduser().absolute()
    if dest.suffix.lower() != ".wav" or dest.resolve() == src:
        raise ValueError("preview output must be a different .wav file")
    if dest.exists() or dest.is_symlink():
        raise FileExistsError(f"preview output already exists: {dest}")
    before = inspect_audio(src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vvh-gain-preview-") as work:
        temp = Path(work) / "preview.wav"
        _decode(src, temp, gain_db=gain_db)
        after = _metrics(temp, ".wav")
        if after["decoded_duration_capped"]:
            raise ValueError("source exceeds 180 seconds; preview refused")
        # A new file is opened exclusively so even concurrent callers cannot
        # overwrite an existing recording. No partial file is retained.
        with dest.open("xb") as result:
            try:
                with temp.open("rb") as stream:
                    shutil.copyfileobj(stream, result, length=65536)
            except BaseException:
                result.close()
                dest.unlink(missing_ok=True)
                raise
    return {
        "schema": "vvh.gain-preview.v1", "output": str(dest),
        "bytes": dest.stat().st_size,
        "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
        "gain_db": gain_db, "before": before, "after": after,
        "creator_manifest_changed": False,
        "install_authorized": False, "redistribution_verified": False,
        "note": "Preview does not replace the source. Listening and licensing review required.",
    }
