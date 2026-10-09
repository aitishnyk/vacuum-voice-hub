"""Offline translation review with exact-script snapshots and attributable claims.

A contributor's approval is a *declaration*, not proof of native fluency,
copyright, audio quality or device install support. This file is local only.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .script_packs import script_for_model
from .translation_overlays import _no_duplicate_keys

SCHEMA = "vvh.language-review.v1"
MAX_BYTES = 256 * 1024
STATUSES = ("pending", "needs-changes", "approved")


def _encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _digest(rows):
    return hashlib.sha256(json.dumps(
        rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _load(path):
    source = Path(path).expanduser()
    if source.is_symlink() or not source.is_file():
        raise ValueError("review must be a regular local file")
    with source.open("rb") as stream:
        payload = stream.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("language review exceeds 256 KiB")
    try:
        doc = json.loads(payload.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid language review JSON") from exc
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise ValueError("unsupported language review schema")
    return doc


def _snapshot(locale, model_id, overlay_path=None):
    script = script_for_model(locale, model_id, overlay_path=overlay_path)
    rows = [{"semantic": r["semantic"], "text": r["text"],
             "translation_source": r["translation_source"],
             "target_event_ids": r["target_event_ids"]}
            for r in script["entries"]]
    if not 1 <= len(rows) <= 512:
        raise ValueError("language review needs 1..512 text entries")
    return script, rows


def _new_file(dest, doc):
    target = Path(dest).expanduser().absolute()
    if target.is_symlink() or target.exists():
        raise FileExistsError("language review output must not exist")
    payload = _encode(doc)
    if len(payload) > MAX_BYTES:
        raise ValueError("language review output exceeds 256 KiB")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as out:
        try:
            out.write(payload)
        except BaseException:
            out.close()
            target.unlink(missing_ok=True)
            raise
    return target


def create_language_review(locale, model_id, output, *, overlay_path=None):
    script, source_rows = _snapshot(locale, model_id, overlay_path)
    doc = {
        "schema": SCHEMA, "locale": script["locale"], "model_id": script["model_id"],
        "source_digest_sha256": _digest(source_rows),
        "requires_overlay_for_audit": overlay_path is not None,
        "source_overlay_count": script["overlay_count"],
        "entries": [{**row, "review": {"status": "pending", "reviewer": None,
                                      "reviewed_at": None, "note": None,
                                      "language_attested": False}}
                    for row in source_rows],
        "human_review_independently_verified": False,
        "audio_files_generated": False, "install_authorized": False,
    }
    dest = _new_file(output, doc)
    return {"schema": SCHEMA, "output": str(dest), "locale": doc["locale"],
            "model_id": doc["model_id"], "entries": len(source_rows),
            "approved": 0, "install_authorized": False}


def audit_language_review(path, *, overlay_path=None):
    doc = _load(path)
    if doc.get("requires_overlay_for_audit") not in (True, False):
        raise ValueError("invalid overlay declaration")
    if doc["requires_overlay_for_audit"] and overlay_path is None:
        raise ValueError("original translation overlay required for audit")
    script, source_rows = _snapshot(doc["locale"], doc["model_id"], overlay_path)
    rows = doc.get("entries")
    if not isinstance(rows, list) or len(rows) != len(source_rows):
        raise ValueError("language review event count differs from current script")
    if doc.get("source_overlay_count") != script["overlay_count"]:
        raise ValueError("language review overlay count changed")
    if doc.get("source_digest_sha256") != _digest(source_rows):
        raise ValueError("language review is stale: script or translation changed")
    counts = {k: 0 for k in STATUSES}
    for row, source in zip(rows, source_rows):
        if not isinstance(row, dict) or any(row.get(k) != v for k, v in source.items()):
            raise ValueError("language review phrase/event mapping changed")
        state = row.get("review")
        if not isinstance(state, dict) or state.get("status") not in STATUSES:
            raise ValueError("invalid language review state")
        status = state["status"]
        counts[status] += 1
        reviewer = state.get("reviewer")
        note = state.get("note")
        if note is not None and (not isinstance(note, str) or len(note) > 500 or
                                any(ord(c) < 32 for c in note)):
            raise ValueError("invalid review note")
        if status == "pending":
            if (reviewer is not None or state.get("reviewed_at") is not None or
                    state.get("language_attested") is not False):
                raise ValueError("pending review cannot declare approval")
        else:
            if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 128:
                raise ValueError("non-pending review requires attributed reviewer")
            timestamp = state.get("reviewed_at")
            if not isinstance(timestamp, str) or len(timestamp) > 64 or not timestamp.endswith("+00:00"):
                raise ValueError("invalid review timestamp")
            if state.get("language_attested") is not (status == "approved"):
                raise ValueError("explicit language attestation required for approval")
    if doc.get("install_authorized") is not False or doc.get("audio_files_generated") is not False:
        raise ValueError("language review cannot authorize install or fabricate audio")
    return {"schema": SCHEMA, "locale": doc["locale"],
            "model_id": doc["model_id"], "entries": len(rows), "counts": counts,
            "source_digest_sha256": doc["source_digest_sha256"], "snapshot_current": True,
            "human_approval_claims": counts["approved"],
            "human_review_independently_verified": False,
            "native_speaker_independently_verified": False,
            "rights_independently_verified": False,
            "install_authorized": False}


def mark_language_review(path, semantic, status, output, *,
                         reviewer=None, note=None, language_attested=False,
                         overlay_path=None):
    if status not in STATUSES:
        raise ValueError("invalid language review status")
    if not isinstance(semantic, str) or not semantic:
        raise ValueError("semantic required")
    if status != "pending":
        if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 128:
            raise ValueError("reviewer required for decision")
    if status == "approved" and language_attested is not True:
        raise ValueError("approval needs explicit language attestation")
    if note is not None and (not isinstance(note, str) or len(note) > 500 or
                            any(ord(c) < 32 for c in note)):
        raise ValueError("review note invalid")
    audit_language_review(path, overlay_path=overlay_path)
    record = _load(path)
    task = next((r for r in record["entries"] if r["semantic"] == semantic), None)
    if task is None:
        raise ValueError("semantic not in reviewed script")
    task["review"] = {
        "status": status,
        "reviewer": reviewer.strip() if status != "pending" else None,
        "reviewed_at": datetime.now(timezone.utc).isoformat() if status != "pending" else None,
        "note": note, "language_attested": status == "approved",
    }
    record["previous_review_sha256"] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    dest = _new_file(output, record)
    return {"schema": SCHEMA, "output": str(dest), "semantic": semantic,
            "status": status, "approved": status == "approved",
            "install_authorized": False}
