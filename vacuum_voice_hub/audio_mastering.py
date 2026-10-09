"""Non-destructive, bounded offline mastering for locally owned robot voice clips.

This produces REVIEW PREVIEWS only. It does not alter a Creator source, claim
redistribution rights or authorize upload to any robot.
"""
import array
import hashlib
import math
import shutil
import sys
import tempfile
import wave
from pathlib import Path

from .audio_advanced import _source, _decode, _metrics
from .audio_qa import inspect_wav, MAX_DURATION_SEC


def _db_to_amplitude(db):
    return 32767 * 10 ** (db / 20)


def _bounded_number(value, low, high, label):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{label} must be a finite number from {low} to {high}")
    v = float(value)
    if not math.isfinite(v) or not low <= v <= high:
        raise ValueError(f"{label} must be a finite number from {low} to {high}")
    return v


def master_preview(source, output, *, target_peak_dbfs=-3.0, silence_dbfs=-45.0,
                   padding_ms=80, fade_ms=8, trim_silence=True):
    """Make a NEW mono 16 kHz WAV preview: trim silence, fade, normalize peak.

    No overwrite, source mutation, vendor transport, network access or automatic
    promotion to a reviewed pack. Decode has the same strict FFmpeg limits as QA.
    """
    target_peak_dbfs = _bounded_number(target_peak_dbfs, -18, -1, "target peak")
    silence_dbfs = _bounded_number(silence_dbfs, -70, -20, "silence threshold")
    padding_ms = _bounded_number(padding_ms, 0, 500, "padding")
    fade_ms = _bounded_number(fade_ms, 0, 200, "fade")
    if type(trim_silence) is not bool:
        raise ValueError("trim_silence must be boolean")
    src = _source(source)
    dest = Path(output).expanduser().absolute()
    if dest.suffix.lower() != ".wav" or dest.resolve() == src:
        raise ValueError("output must be a different WAV path")
    if dest.exists() or dest.is_symlink():
        raise FileExistsError(f"output already exists: {dest}")
    initial_sha256 = hashlib.sha256(src.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="vvh-master-preview-") as tempdir:
        decoded = Path(tempdir) / "decoded.wav"
        candidate = Path(tempdir) / "master.wav"
        _decode(src, decoded)
        before = _metrics(decoded, src.suffix.lower())
        if before["decoded_duration_capped"] or before["signal"]["duration_sec"] > MAX_DURATION_SEC:
            raise ValueError("source exceeds 180-second maximum")
        with wave.open(str(decoded), "rb") as inp:
            if (inp.getnchannels(), inp.getsampwidth(), inp.getframerate(), inp.getcomptype()) != (1, 2, 16000, "NONE"):
                raise ValueError("decoded WAV must be mono 16-bit PCM at 16 kHz")
            sample_count = inp.getnframes()
            samples = array.array("h")
            samples.frombytes(inp.readframes(sample_count))
            if len(samples) != sample_count:
                raise ValueError("truncated decoded source")
            if sys.byteorder != "little":
                samples.byteswap()
        if not samples:
            raise ValueError("empty decoded source")
        original_samples = len(samples)
        threshold = _db_to_amplitude(silence_dbfs)
        # Find boundaries without materializing up to 2.9 million Python indices.
        first = next((i for i, sample in enumerate(samples)
                      if abs(sample) >= threshold), None)
        if first is None:
            raise ValueError("no audio above the silence threshold")
        last = next(i for i in range(len(samples) - 1, -1, -1)
                    if abs(samples[i]) >= threshold)
        if trim_silence:
            pad_frames = round(padding_ms * 16)
            start = max(0, first - pad_frames)
            end = min(len(samples), last + 1 + pad_frames)
            samples = samples[start:end]
        else:
            start, end = 0, len(samples)
        if not samples or len(samples) / 16000 < 0.25:
            raise ValueError("processed clip would be shorter than 0.25 seconds")
        peak = max(abs(x) for x in samples)
        if not peak:
            raise ValueError("no usable audio")
        gain = _db_to_amplitude(target_peak_dbfs) / peak
        # Avoid boosting background hiss from nearly silent source material.
        if gain > 10 ** (12 / 20):
            raise ValueError("source is too quiet for safe automatic mastering (+12 dB limit)")
        fade_frames = min(round(fade_ms * 16), len(samples) // 2)
        processed = array.array("h")
        for idx, sample in enumerate(samples):
            factor = 1.0
            if fade_frames:
                if idx < fade_frames:
                    factor = min(factor, (idx + 1) / fade_frames)
                if idx >= len(samples) - fade_frames:
                    factor = min(factor, (len(samples) - idx) / fade_frames)
            value = round(sample * gain * factor)
            processed.append(max(-32768, min(32767, value)))
        if sys.byteorder != "little":
            processed.byteswap()
        with wave.open(str(candidate), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(processed.tobytes())
        after = inspect_wav(candidate)
        if "clipping" in after["warnings"]:
            raise ValueError("mastered output contains clipping")
        # The input must not silently change during decode/mastering.
        if hashlib.sha256(src.read_bytes()).hexdigest() != initial_sha256:
            raise ValueError("source recording changed during mastering")
        # Destination creation is exclusive, and any partial output is removed.
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("xb") as file:
            try:
                with candidate.open("rb") as data:
                    shutil.copyfileobj(data, file, length=65536)
            except BaseException:
                file.close()
                dest.unlink(missing_ok=True)
                raise
    return {
        "schema": "vvh.master-preview.v1",
        "source_sha256": initial_sha256,
        "source_format": src.suffix.lower(),
        "output": str(dest), "output_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
        "bytes": dest.stat().st_size,
        "target_peak_dbfs": target_peak_dbfs, "silence_dbfs": silence_dbfs,
        "trim_silence": trim_silence,
        "padding_ms": padding_ms, "fade_ms": fade_ms,
        "removed_leading_frames": start,
        "removed_trailing_frames": original_samples - end,
        "before": before, "after": after,
        "creator_manifest_changed": False, "install_authorized": False,
        "redistribution_verified": False,
        "human_review_required": True,
    }
