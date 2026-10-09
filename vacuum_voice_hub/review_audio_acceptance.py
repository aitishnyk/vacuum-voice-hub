"""Read-only, bounded clip-by-clip signal QC aligned with human review.

An approved reviewer statement and good signal statistics remain separate.
No language/rights/hardware verification is inferred.
"""
from pathlib import Path

from .production_review import _load_json, audit_review
from .review_history import audit_review_history

SCHEMA = "vvh.review-audio-acceptance.v1"


def inspect_review_audio(review_path, *, max_clips=16, decode_compressed=False,
                         overlay_path=None):
    if type(max_clips) is not int or not 1 <= max_clips <= 32:
        raise ValueError("max_clips must be 1..32")
    reviewed = audit_review(review_path, overlay_path=overlay_path)
    if not reviewed["valid"]:
        raise ValueError("review has stale or mismatched audio snapshots")
    audit_review_history(review_path)
    record = _load_json(review_path)
    root = Path(record["workspace"]).resolve()
    rows = [r for r in record["tasks"] if r["audio"]]
    selected = rows[:max_clips]
    clips = []
    for row in selected:
        path = (root / row["audio"]["file"]).resolve()
        path.relative_to(root)
        suffix = path.suffix.lower()
        result = {
            "semantic": row["semantic"],
            "audio_sha256": row["audio"]["sha256"],
            "human_review_status": row["review"]["status"],
            "human_rights_attested": row["review"]["rights_attested"] is True,
            "signal_status": "not-analyzed",
        }
        if suffix == ".wav" or decode_compressed:
            try:
                from .audio_advanced import inspect_audio
                qa = inspect_audio(path)
                result["signal_status"] = "inspected"
                result["source_format"] = qa["source_format"]
                result["signal"] = qa["signal"]
                result["signal_warnings"] = qa["warnings"]
                result["signal_basic_pass"] = qa["pass_basic_checks"]
            except ValueError as exc:
                result["signal_status"] = "invalid"
                result["signal_warnings"] = ["invalid-audio"]
                result["signal_error"] = str(exc)
                result["signal_basic_pass"] = False
        clips.append(result)
    return {
        "schema": SCHEMA,
        "model_id": record["model_id"], "locale": record["locale"],
        "total_recorded": len(rows), "inspected": sum(
            x["signal_status"] == "inspected" for x in clips),
        "not_analyzed": sum(x["signal_status"] == "not-analyzed" for x in clips),
        "invalid": sum(x["signal_status"] == "invalid" for x in clips),
        "signal_passed": sum(x.get("signal_basic_pass") is True for x in clips),
        "human_approved": sum(r["review"]["status"] == "approved" for r in rows),
        "returned_clips": len(clips),
        "remaining_uninspected": max(0, len(rows) - len(selected)),
        "decode_compressed_requested": decode_compressed,
        "clips": clips,
        "speaker_language_automatically_verified": False,
        "rights_independently_verified": False,
        "install_authorized": False,
    }
