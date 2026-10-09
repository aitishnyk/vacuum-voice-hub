"""Offline human recording checklist and tamper-aware review workflow.

Declarations and human attestations are not independent verification of
pronunciation, copyright ownership or robot installation compatibility.
"""
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from .catalog import event_by_id, event_profile_for_model, model_by_id
from .creator import MAX_AUDIO_BYTES, validate_workspace
from .script_packs import script_for_model

SCHEMA = "vvh.production-review.v1"
MAX_REVIEW_BYTES = 512 * 1024
MAX_ROWS = 512
MAX_BUNDLE_BYTES = 100 * 1024 * 1024
STATUSES = ("draft", "recorded", "listened", "approved")


def _hash(path):
    sha = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _load_json(path):
    p = Path(path).expanduser()
    if not p.is_file() or p.stat().st_size > MAX_REVIEW_BYTES:
        raise ValueError("review manifest missing or larger than 512 KiB")
    def pairs(values):
        obj = {}
        for key, value in values:
            if key in obj:
                raise ValueError(f"duplicate review JSON key: {key}")
            obj[key] = value
        return obj
    try:
        return json.loads(p.read_text("utf-8"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError("invalid review JSON") from e


def _audio_snapshot(root, rel):
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError("unsafe recording path")
    p = (root / rel).resolve()
    p.relative_to(root)
    if not p.is_file() or not 0 < p.stat().st_size <= MAX_AUDIO_BYTES:
        raise ValueError("recording missing or exceeds 25 MiB")
    return {"file": rel, "bytes": p.stat().st_size, "sha256": _hash(p)}


def _snapshot(path, locale, model_id, overlay_path=None):
    validation = validate_workspace(path)
    # Planning a voice production checklist must work before the first
    # recording exists. All other Creator validation failures remain fatal.
    fatal = [error for error in validation["errors"]
             if error != "events must contain at least one semantic audio mapping"]
    if fatal:
        raise ValueError("invalid Creator workspace: " + "; ".join(fatal))
    root = Path(validation["workspace"]).resolve()
    manifest = validation["manifest"]
    target = model_by_id(model_id)
    script = script_for_model(locale, target["id"], overlay_path)
    profile = event_profile_for_model(target["id"])
    known_ids = set(profile["known_event_ids"])
    scripted = {e["semantic"]: e for e in script["entries"] if e["target_event_ids"]}
    # Include the full target profile, not just the 16 translated text prompts.
    index = {}
    for event_id in sorted(known_ids):
        event = event_by_id(event_id)
        row = index.setdefault(event["semantic"], {
            "semantic": event["semantic"], "event_ids": [],
            "text": scripted.get(event["semantic"], {}).get("text"),
            "text_source": scripted.get(event["semantic"], {}).get("translation_source"),
            "english_reference_not_translated": event.get("description", ""),
        })
        row["event_ids"].append(event_id)
    if len(index) > MAX_ROWS:
        raise ValueError("model has more than 512 distinct recording tasks")
    rows = []
    for semantic in sorted(index):
        row = index[semantic]
        rel = manifest["events"].get(semantic)
        row["audio"] = _audio_snapshot(root, rel) if rel else None
        row["review"] = {"status": "draft", "reviewer": None, "reviewed_at": None,
                         "note": None, "language_attested": False,
                         "rights_attested": False}
        rows.append(row)
    return root, manifest, target, script, rows


def create_review(workspace, locale, model_id, output, *, overlay_path=None):
    root, manifest, target, script, rows = _snapshot(workspace, locale, model_id, overlay_path)
    review = {
        "schema": SCHEMA, "workspace": str(root), "pack_id": manifest["id"],
        "model_id": target["id"], "locale": locale,
        "workspace_manifest_sha256": _hash(root / "manifest.json"),
        "text_script_digest": hashlib.sha256(json.dumps(
            [(r["semantic"], r["event_ids"], r["text"]) for r in rows],
            ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
        "overlay_required_for_audit": overlay_path is not None,
        "tasks": rows, "install_authorized": False,
        "license_automatically_verified": False,
        "speaker_language_automatically_verified": False,
    }
    dest = Path(output).expanduser().absolute()
    if dest.resolve() == root / "manifest.json" or root in dest.resolve().parents:
        raise ValueError("review file must be outside the Creator workspace")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("x", encoding="utf-8") as f:
        json.dump(review, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return {"file": str(dest), "total_tasks": len(rows),
            "text_ready": sum(x["text"] is not None for x in rows),
            "audio_present": sum(x["audio"] is not None for x in rows),
            "schema": SCHEMA, "install_authorized": False}


def audit_review(review_path, *, workspace=None, overlay_path=None):
    review = _load_json(review_path)
    if not isinstance(review, dict) or review.get("schema") != SCHEMA:
        raise ValueError("unsupported review manifest")
    root = Path(workspace or review.get("workspace", "")).expanduser().resolve()
    _, manifest, target, script, fresh = _snapshot(root, review["locale"], review["model_id"], overlay_path)
    tasks = review.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != len(fresh):
        raise ValueError("review tasks do not match model profile")
    if review.get("pack_id") != manifest["id"] or review.get("model_id") != target["id"]:
        raise ValueError("review pack/model mismatch")
    expected_digest = hashlib.sha256(json.dumps(
        [(r["semantic"], r["event_ids"], r["text"]) for r in fresh],
        ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    stale = review.get("workspace_manifest_sha256") != _hash(root / "manifest.json") or review.get("text_script_digest") != expected_digest or (review.get("overlay_required_for_audit") and overlay_path is None)
    issues = []
    counts = {status: 0 for status in STATUSES}
    audio_present = 0
    approved_valid = 0
    for existing, expected in zip(tasks, fresh):
        semantic = expected["semantic"]
        if (not isinstance(existing, dict) or existing.get("semantic") != semantic or
            existing.get("event_ids") != expected["event_ids"] or
            existing.get("text") != expected["text"]):
            raise ValueError(f"review task identity/text altered: {semantic}")
        state = existing.get("review")
        if not isinstance(state, dict) or state.get("status") not in STATUSES:
            raise ValueError(f"invalid review status: {semantic}")
        status = state["status"]
        counts[status] += 1
        actual = expected["audio"]
        if actual:
            audio_present += 1
        if existing.get("audio") != actual:
            issues.append({"semantic": semantic, "issue": "audio-snapshot-mismatch"})
            continue
        if status != "draft" and not actual:
            issues.append({"semantic": semantic, "issue": "review-without-recording"})
            continue
        if status in ("listened", "approved") and not _reviewer(state.get("reviewer")):
            issues.append({"semantic": semantic, "issue": "reviewer-required"})
            continue
        if status == "approved":
            if not (state.get("language_attested") is True and state.get("rights_attested") is True):
                issues.append({"semantic": semantic, "issue": "attestations-required"})
            else:
                approved_valid += 1
    if stale:
        issues.append({"issue": "workspace-or-script-snapshot-changed"})
    return {
        "schema": SCHEMA, "workspace": str(root), "model_id": target["id"],
        "locale": review["locale"], "pack_id": manifest["id"],
        "total_tasks": len(fresh), "audio_present": audio_present,
        "text_ready": sum(r["text"] is not None for r in fresh),
        "status_counts": counts, "approved_with_matching_audio": approved_valid if not issues else 0,
        "issues": issues, "snapshot_current": not stale,
        "valid": not issues, "human_attestation_recorded": counts["approved"] > 0,
        "independent_rights_verified": False,
        "independent_language_verified": False,
        "install_authorized": False,
    }


def _reviewer(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 128


def mark_review(review_path, semantic, status, *, reviewer=None, note=None,
                language_attested=False, rights_attested=False, overlay_path=None):
    if status not in STATUSES:
        raise ValueError("status must be draft, recorded, listened or approved")
    # Journal validation must happen before editing a previously reviewed file.
    from .review_history import audit_review_history, append_review_history
    audit_review_history(review_path)
    # Never write a changed/stale review manifest or accept an out-of-sequence approval.
    check = audit_review(review_path, overlay_path=overlay_path)
    if not check["valid"]:
        raise ValueError("review manifest stale or invalid: " + str(check["issues"][:3]))
    path = Path(review_path).expanduser().resolve()
    record = _load_json(path)
    target = next((r for r in record["tasks"] if r["semantic"] == semantic), None)
    if target is None:
        raise ValueError("semantic not in this model review checklist")
    previous = target["review"]["status"]
    transitions = {"draft": {"draft", "recorded"}, "recorded": {"draft", "listened"},
                   "listened": {"draft", "approved"}, "approved": {"draft"}}
    if status not in transitions[previous]:
        raise ValueError(f"invalid review transition {previous} -> {status}")
    if status != "draft" and not target["audio"]:
        raise ValueError("recording required for review advancement")
    if status in ("listened", "approved") and not _reviewer(reviewer):
        raise ValueError("human reviewer identifier required")
    if note is not None and (not isinstance(note, str) or len(note) > 500):
        raise ValueError("review note must be <=500 characters")
    if status == "approved" and (language_attested is not True or rights_attested is not True):
        raise ValueError("explicit human language and rights attestations required")
    # Status is a signed-off *claim*, not machine verification or a rights grant.
    target["review"] = {
        "status": status,
        "reviewer": reviewer.strip() if reviewer else None,
        "reviewed_at": datetime.now(timezone.utc).isoformat() if status in ("listened", "approved") else None,
        "note": note, "language_attested": status == "approved",
        "rights_attested": status == "approved",
    }
    _write_review(path, record)
    journal = append_review_history(path, "review-mark", {
        "semantic": semantic, "from": previous, "to": status,
        "reviewer": reviewer.strip() if reviewer else None,
    })
    return {"semantic": semantic, "status": status,
            "audit": audit_review(path, overlay_path=overlay_path),
            "journal": journal, "install_authorized": False}


def export_review_bundle(review_path, output, *, include_audio=False, overlay_path=None):
    audit = audit_review(review_path, overlay_path=overlay_path)
    if not audit["valid"]:
        raise ValueError("cannot export stale or invalid review")
    record = _load_json(review_path)
    root = Path(record["workspace"]).resolve()
    dest = Path(output).expanduser().absolute()
    if dest.suffix.lower() != ".zip" or root in dest.resolve().parents:
        raise ValueError("bundle output must be a new external .zip")
    if dest.exists() or dest.is_symlink():
        raise FileExistsError("review bundle output already exists")
    export = {k: v for k, v in record.items() if k != "workspace"}
    export["audio_included"] = bool(include_audio)
    export["install_authorized"] = False
    export["human_review_not_independent_verification"] = True
    dest.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with dest.open("xb") as stream:
            created = True
            with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr("review.json", json.dumps(export, ensure_ascii=False, indent=2) + "\n")
                z.writestr("audit.json", json.dumps({k: v for k, v in audit.items() if k != "workspace"},
                                                   ensure_ascii=False, indent=2) + "\n")
                if include_audio:
                    seen = set()
                    total = 0
                    for task in record["tasks"]:
                        item = task["audio"]
                        if not item or item["file"] in seen:
                            continue
                        seen.add(item["file"])
                        src = (root / item["file"]).resolve()
                        src.relative_to(root)
                        if _audio_snapshot(root, item["file"]) != item:
                            raise ValueError("recording changed during bundle export")
                        total += item["bytes"]
                        if total > MAX_BUNDLE_BYTES:
                            raise ValueError("review audio bundle exceeds 100 MiB")
                        z.write(src, "audio/" + item["file"])
        if include_audio:
            # Catch local file edits that race with the archive reader after
            # the pre-copy source hash was checked.
            with zipfile.ZipFile(dest) as verify:
                for task in record["tasks"]:
                    item = task["audio"]
                    if item and hashlib.sha256(
                            verify.read("audio/" + item["file"])).hexdigest() != item["sha256"]:
                        raise ValueError("recording changed during review ZIP export")
        return {"file": str(dest), "schema": SCHEMA, "audio_included": bool(include_audio),
                "bytes": dest.stat().st_size, "sha256": _hash(dest),
                "install_authorized": False, "rights_verified": False}
    except BaseException:
        if created:
            dest.unlink(missing_ok=True)
        raise


def refresh_review(review_path, *, overlay_path=None):
    """Refresh recording assignments; preserve approvals only for identical audio/text.

    A changed recording or text always resets that task to draft. A modified
    source manifest cannot silently inherit a previous sign-off.
    """
    from .review_history import audit_review_history, append_review_history
    audit_review_history(review_path)
    path = Path(review_path).expanduser().resolve()
    record = _load_json(path)
    if record.get("schema") != SCHEMA:
        raise ValueError("unsupported review schema")
    root, manifest, target, script, rows = _snapshot(
        record["workspace"], record["locale"], record["model_id"], overlay_path)
    if record.get("pack_id") != manifest["id"]:
        raise ValueError("workspace identity changed")
    if record.get("overlay_required_for_audit") and overlay_path is None:
        raise ValueError("original translation overlay required for refresh")
    old = {r["semantic"]: r for r in record["tasks"]}
    retained = 0
    reset = 0
    for row in rows:
        prev = old.get(row["semantic"])
        if (prev and prev.get("event_ids") == row["event_ids"]
                and prev.get("text") == row["text"]
                and prev.get("audio") == row["audio"]):
            row["review"] = prev["review"]
            retained += 1
        else:
            reset += 1
    record["tasks"] = rows
    record["workspace_manifest_sha256"] = _hash(root / "manifest.json")
    record["text_script_digest"] = hashlib.sha256(json.dumps(
        [(r["semantic"], r["event_ids"], r["text"]) for r in rows],
        ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    _write_review(path, record)
    journal = append_review_history(path, "review-refresh", {
        "retained": retained, "reset": reset,
    })
    result = audit_review(path, overlay_path=overlay_path)
    return {"retained": retained, "reset": reset, "audit": result,
            "journal": journal, "install_authorized": False}


def _write_review(path, record):
    """Exclusive temporary write and atomic replace after bounded validation."""
    payload = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    if len(payload.encode("utf-8")) > MAX_REVIEW_BYTES:
        raise ValueError("review manifest exceeds 512 KiB")
    import os
    import tempfile
    path = Path(path)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=".vvh-review-", delete=False) as tmp:
        name = Path(tmp.name)
        tmp.write(payload)
        tmp.flush()
        os.fsync(tmp.fileno())
    try:
        os.replace(name, path)
    finally:
        name.unlink(missing_ok=True)
