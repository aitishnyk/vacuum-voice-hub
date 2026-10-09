"""Read-only A/B evaluation of two user-provided local audio clips.

The output contains engineering metrics only, never listening/rights approvals.
"""
import hashlib
from .audio_advanced import _source, inspect_audio


def _sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compare_audio(first, second):
    a, b = _source(first), _source(second)
    if a == b:
        raise ValueError("A/B comparison requires two different local files")
    a_sha, b_sha = _sha(a), _sha(b)
    a_report, b_report = inspect_audio(a), inspect_audio(b)
    if a_sha != _sha(a) or b_sha != _sha(b):
        raise ValueError("source changed during read-only audio comparison")
    x, y = a_report["signal"], b_report["signal"]
    def delta(field):
        return (round(y[field] - x[field], 3)
                if x[field] is not None and y[field] is not None else None)
    return {
        "schema": "vvh.audio-ab-review.v1",
        "a": {"sha256": a_sha, "format": a_report["source_format"], "signal": x,
              "warnings": a_report["warnings"]},
        "b": {"sha256": b_sha, "format": b_report["source_format"], "signal": y,
              "warnings": b_report["warnings"]},
        "b_minus_a": {"duration_sec": delta("duration_sec"),
                      "peak_dbfs": delta("peak_dbfs"),
                      "rms_dbfs": delta("rms_dbfs"),
                      "clipped_pct": delta("clipped_pct"),
                      "silent_pct": delta("silent_pct")},
        "comparison_is_read_only": True,
        "human_listening_required": True, "rights_verified": False,
        "source_audio_modified": False, "install_authorized": False,
    }
