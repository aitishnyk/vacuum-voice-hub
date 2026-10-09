"""Read-only bounded audio quality diagnostics for Creator Studio WAV files.

Pure Python, no cloud services and no modifications. Scores are engineering
warnings, not proof of speech intelligibility or model/device compatibility.
"""
import json
import math
import struct
import wave
from pathlib import Path

MAX_AUDIO_BYTES = 25 * 1024 * 1024
MAX_DURATION_SEC = 180
MIN_DURATION_SEC = 0.25
SILENCE_PEAK = 100  # ~ -50 dBFS on 16-bit PCM
CLIPPING_PEAK = 32760


def inspect_wav(path):
    """Analyze mono/stereo signed 16-bit WAV PCM in bounded streaming chunks."""
    p = Path(path).expanduser()
    if not p.is_file() or p.stat().st_size > MAX_AUDIO_BYTES:
        raise ValueError("WAV file missing or exceeds 25 MiB")
    try:
        with wave.open(str(p), "rb") as reader:
            channels = reader.getnchannels()
            width = reader.getsampwidth()
            sample_rate = reader.getframerate()
            frame_count = reader.getnframes()
            compression = reader.getcomptype()
            if not (1 <= channels <= 2) or width != 2 or compression != "NONE" or not (8000 <= sample_rate <= 96000):
                raise ValueError("only 16-bit mono/stereo uncompressed PCM WAV (8–96 kHz) is supported")
            if frame_count < 1 or frame_count > (MAX_AUDIO_BYTES // (channels * width)):
                raise ValueError("empty or oversized WAV frames")
            duration = frame_count / sample_rate
            sum_sq = peak = silent = clipped = total = 0
            while total < frame_count * channels:
                frames = reader.readframes(min(8192, frame_count - total // channels))
                if not frames or len(frames) % 2:
                    raise ValueError("truncated or malformed PCM WAV")
                count = len(frames) // 2
                if count > (frame_count * channels - total):
                    raise ValueError("PCM WAV contains extra frames")
                # Avoid a huge argument expansion and large in-memory decoded arrays.
                for sample in struct.iter_unpack("<h", frames):
                    value = abs(sample[0])
                    peak = max(peak, value)
                    sum_sq += value * value
                    silent += value <= SILENCE_PEAK
                    clipped += value >= CLIPPING_PEAK
                total += count
            if total != frame_count * channels:
                raise ValueError("truncated PCM WAV")
    except (EOFError, OSError, wave.Error, struct.error) as exc:
        raise ValueError("invalid WAV audio") from exc
    rms = math.sqrt(sum_sq / total) if total else 0
    rms_dbfs = round(20 * math.log10(rms / 32768), 1) if rms else None
    peak_dbfs = round(20 * math.log10(peak / 32768), 1) if peak else None
    clipped_pct = round(clipped * 100 / total, 3)
    silent_pct = round(silent * 100 / total, 1)
    warnings = []
    if duration < MIN_DURATION_SEC:
        warnings.append("too-short")
    if duration > MAX_DURATION_SEC:
        warnings.append("too-long")
    if peak == 0 or rms_dbfs is None or rms_dbfs < -42:
        warnings.append("very-quiet")
    if clipped_pct > 0.1:
        warnings.append("clipping")
    if silent_pct > 95:
        warnings.append("mostly-silence")
    return {
        "schema": "vvh.wav-audio-qa.v1",
        "format": "pcm_s16le", "sample_rate": sample_rate, "channels": channels,
        "duration_sec": round(duration, 3), "frames": frame_count,
        "peak_dbfs": peak_dbfs, "rms_dbfs": rms_dbfs,
        "clipped_pct": clipped_pct, "silent_pct": silent_pct,
        "warnings": warnings, "pass_basic_checks": not warnings,
        "note": "Signal-level heuristics only; human listening and device acceptance still required.",
    }


def inspect_workspace(path, model_id=None):
    """Read-only coverage and audio QA for user-supplied Creator workspaces."""
    from .creator import validate_workspace, workspace_model_coverage
    validated = validate_workspace(path)
    root = Path(validated["workspace"]).resolve()
    rows = []
    if not validated["ok"]:
        return {"schema":"vvh.workspace-audio-qa.v1","ok":False,
                "validation_errors":validated["errors"],"audio":rows,
                "install_authorized":False}
    for semantic, rel in sorted(validated["manifest"]["events"].items()):
        file_path = (root / rel).resolve()
        file_path.relative_to(root)
        if file_path.suffix.lower() != ".wav":
            rows.append({"semantic":semantic,"status":"not-analyzed","format":file_path.suffix.lower(),
                         "note":"WAV-only signal QA; normalize to 16-bit PCM WAV to inspect"})
            continue
        try:
            info = inspect_wav(file_path)
            rows.append({"semantic":semantic,"status":"inspected",**info})
        except ValueError as exc:
            rows.append({"semantic":semantic,"status":"invalid","error":str(exc)})
    checked = [x for x in rows if x["status"]=="inspected"]
    errors = [x for x in rows if x["status"]=="invalid"]
    warnings = [x for x in checked if x["warnings"]]
    return {
        "schema":"vvh.workspace-audio-qa.v1",
        "ok":not errors and not warnings,
        "validation_errors":[],
        "audio":rows,
        "analyzed_wav":len(checked),
        "unanalysed_formats":sum(x["status"]=="not-analyzed" for x in rows),
        "warnings_count":len(warnings),
        "errors_count":len(errors),
        "coverage":workspace_model_coverage(root,model_id) if model_id else None,
        "install_authorized":False,
    }
