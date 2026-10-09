"""Offline, non-destructive sound-wave overview and exact local clip selection.

Creator sources are immutable; all exports are standalone review WAV files.
"""
import array
import hashlib
import math
import shutil
import sys
import tempfile
import wave
from pathlib import Path

from .audio_advanced import _decode, _source
from .audio_mastering import _bounded_number
from .audio_qa import inspect_wav, MAX_DURATION_SEC


def _sha256(path):
    sha = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(65536), b""):
            sha.update(block)
    return sha.hexdigest()


def _samples(decoded):
    with wave.open(str(decoded), "rb") as wav:
        if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getcomptype()) != (1, 2, 16000, "NONE"):
            raise ValueError("decoded audio must be mono 16-bit 16 kHz PCM")
        count = wav.getnframes()
        if not 1 <= count <= 16000 * 181:
            raise ValueError("decoded clip exceeds maximum size")
        raw = wav.readframes(count)
    values = array.array("h")
    values.frombytes(raw)
    if sys.byteorder != "little":
        values.byteswap()
    if len(values) != count or not values:
        raise ValueError("invalid or truncated decoded PCM")
    if count / 16000 > MAX_DURATION_SEC:
        raise ValueError("clip exceeds 180 second limit")
    return values


def _prepare(source):
    if Path(source).expanduser().is_symlink():
        raise ValueError("symlinked source audio refused")
    src = _source(source)
    return src, _sha256(src)


def audio_timeline(source, *, bins=256):
    """Return at most 512 normalized waveform bins, never audio samples."""
    if type(bins) is not int or not 16 <= bins <= 512:
        raise ValueError("timeline bins must be 16..512")
    src, original_sha = _prepare(source)
    with tempfile.TemporaryDirectory(prefix="vvh-timeline-") as scratch:
        decoded = Path(scratch) / "clip.wav"
        _decode(src, decoded)
        values = _samples(decoded)
        total = len(values)
        group = math.ceil(total / bins)
        peaks = [round(max(abs(x) for x in values[i:min(i+group,total)]) / 32768, 4)
                 for i in range(0, total, group)]
        duration = round(total / 16000, 4)
    if _sha256(src) != original_sha:
        raise ValueError("source audio changed during timeline inspection")
    return {
        "schema": "vvh.audio-timeline.v1", "source_sha256": original_sha,
        "source_format": src.suffix.lower(), "duration_sec": duration,
        "sample_rate": 16000, "peak_bins": peaks, "bin_count": len(peaks),
        "source_mutated": False, "audio_output_created": False,
        "human_review_required": True, "install_authorized": False,
    }


def cut_preview(source, output, *, start_ms, end_ms, fade_ms=8):
    """Export selected range as NEW PCM WAV; never overwrite or reassign."""
    start = _bounded_number(start_ms, 0, 180000, "start time")
    end = _bounded_number(end_ms, 0, 180000, "end time")
    fade = _bounded_number(fade_ms, 0, 200, "fade")
    if end - start < 250:
        raise ValueError("selected segment must be at least 250 ms")
    src, original_sha = _prepare(source)
    dest = Path(output).expanduser().absolute()
    if dest.suffix.lower() != ".wav" or dest.resolve() == src:
        raise ValueError("output must be a different WAV path")
    if dest.exists() or dest.is_symlink():
        raise FileExistsError("selected output already exists")
    with tempfile.TemporaryDirectory(prefix="vvh-cut-preview-") as scratch:
        decoded = Path(scratch) / "clip.wav"
        candidate = Path(scratch) / "selection.wav"
        _decode(src, decoded)
        values = _samples(decoded)
        first, last = round(start * 16), round(end * 16)
        if first >= len(values) or last > len(values) or last <= first:
            raise ValueError("selection outside actual audio duration")
        selected = values[first:last]
        if len(selected) < 4000:
            raise ValueError("selected output is shorter than 250 ms")
        fade_frames = min(round(fade * 16), len(selected) // 2)
        if fade_frames:
            for index in range(fade_frames):
                factor = (index + 1) / fade_frames
                selected[index] = round(selected[index] * factor)
                last_index = len(selected) - 1 - index
                selected[last_index] = round(selected[last_index] * factor)
        if sys.byteorder != "little":
            selected.byteswap()
        with wave.open(str(candidate), "wb") as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(16000)
            wav.writeframes(selected.tobytes())
        qa = inspect_wav(candidate)
        if _sha256(src) != original_sha:
            raise ValueError("source audio changed during preview export")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("xb") as stream:
            try:
                with candidate.open("rb") as data:
                    shutil.copyfileobj(data, stream, length=65536)
            except BaseException:
                stream.close()
                dest.unlink(missing_ok=True)
                raise
    return {
        "schema": "vvh.audio-cut-preview.v1", "source_sha256": original_sha,
        "output": str(dest), "output_sha256": _sha256(dest),
        "start_ms": start, "end_ms": end, "fade_ms": fade,
        "quality": qa, "creator_manifest_changed": False,
        "source_mutated": False, "human_review_required": True,
        "redistribution_verified": False, "install_authorized": False,
    }
