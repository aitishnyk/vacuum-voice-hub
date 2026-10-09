"""Offline copy-on-write moderation of submitted hardware-research metadata.

No server, uploader, robot access, device approvals or source evidence storage.
Snapshots are self-checksummed and decisions form a hash-linked local history;
neither is a cryptographic signature or independently verified testimony.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .catalog import model_by_id
from .community_testkit import _FIRMWARE
from .firmware_matrix import _read_report
from .hardware_acceptance import FIELDS
from .translation_overlays import _no_duplicate_keys

SCHEMA = "vvh.community-inbox.v1"
MAX_BYTES = 512 * 1024
MAX_ITEMS = 256
SHA = re.compile(r"^[0-9a-f]{64}$")
DECISIONS = frozenset(("research-accepted", "needs-evidence", "rejected"))
ZERO_SHA = "0" * 64


def _bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def _sealable(doc):
    return {k: v for k, v in doc.items() if k != "snapshot_sha256"}


def _text(value, *, size=128):
    return (isinstance(value, str) and 1 <= len(value.strip()) <= size
            and value == value.strip()
            and all(ord(c) >= 32 and ord(c) != 127 for c in value))


def _read(path):
    p = Path(path).expanduser()
    if p.is_symlink() or not p.is_file():
        raise ValueError("inbox must be an existing regular file")
    with p.open("rb") as stream:
        b = stream.read(MAX_BYTES + 1)
    if not 1 <= len(b) <= MAX_BYTES:
        raise ValueError("inbox size invalid or exceeds 512 KiB")
    try:
        doc = json.loads(b.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid inbox JSON") from exc
    _audit(doc)
    return doc


def _audit(doc):
    if not isinstance(doc, dict) or set(doc) != {
        "schema", "submissions", "reviews", "previous_snapshot_sha256",
        "snapshot_sha256", "install_authorized", "independent_device_verified",
    } or doc["schema"] != SCHEMA:
        raise ValueError("invalid community inbox schema")
    if doc["install_authorized"] is not False or doc["independent_device_verified"] is not False:
        raise ValueError("community inbox cannot certify any device")
    if doc["previous_snapshot_sha256"] is not None and not SHA.fullmatch(str(doc["previous_snapshot_sha256"])):
        raise ValueError("invalid previous snapshot hash")
    if not SHA.fullmatch(str(doc["snapshot_sha256"])) or _sha(_sealable(doc)) != doc["snapshot_sha256"]:
        raise ValueError("inbox snapshot checksum mismatch")
    items = doc["submissions"]
    reviews = doc["reviews"]
    if not isinstance(items, list) or not isinstance(reviews, list):
        raise ValueError("community inbox requires arrays")
    if len(items) > MAX_ITEMS or len(reviews) > MAX_ITEMS:
        raise ValueError("community inbox maximum of 256 submissions exceeded")
    known = {}
    for item in items:
        if not isinstance(item, dict) or set(item) != {
            "id", "model_id", "firmware", "package_sha256",
            "observed_steps", "self_report_status", "source_report_sha256",
        }:
            raise ValueError("invalid redacted community submission")
        for key in ("id", "package_sha256", "source_report_sha256"):
            if not isinstance(item[key], str) or not SHA.fullmatch(item[key]):
                raise ValueError("invalid community evidence hash")
        canonical = model_by_id(item["model_id"])
        if canonical["id"] != item["model_id"]:
            raise ValueError("alias cannot be used as community device identity")
        if not isinstance(item["firmware"], str) or not _FIRMWARE.fullmatch(item["firmware"]):
            raise ValueError("invalid firmware field")
        steps = item["observed_steps"]
        if not isinstance(steps, list) or steps != sorted(set(steps)) or set(steps) - set(FIELDS):
            raise ValueError("invalid observed steps")
        if item["self_report_status"] not in {
            "ready-for-independent-hardware-review", "incomplete-research-only"
        }:
            raise ValueError("invalid untrusted self-report status")
        if item["id"] != item["source_report_sha256"] or item["id"] in known:
            raise ValueError("duplicate or inconsistent community submission")
        known[item["id"]] = item
    decided = set()
    prev = ZERO_SHA
    for seq, event in enumerate(reviews, 1):
        if not isinstance(event, dict) or set(event) != {
            "sequence", "submission_id", "decision", "reviewer",
            "note", "timestamp", "previous_decision_sha256", "decision_sha256",
        }:
            raise ValueError("invalid community review record")
        if type(event["sequence"]) is not int or event["sequence"] != seq:
            raise ValueError("community review history sequence invalid")
        ref = event["submission_id"]
        if ref not in known or ref in decided:
            raise ValueError("review for missing or already moderated submission")
        if event["decision"] not in DECISIONS:
            raise ValueError("unknown community review decision")
        if not _text(event["reviewer"]) or not _text(event["note"], size=240):
            raise ValueError("reviewer and nonempty short note required")
        stamp = event["timestamp"]
        if not isinstance(stamp, str) or len(stamp) > 64 or not stamp.endswith("+00:00"):
            raise ValueError("review timestamp invalid")
        if event["previous_decision_sha256"] != prev:
            raise ValueError("community review decision chain broken")
        if not isinstance(event["decision_sha256"], str) or not SHA.fullmatch(event["decision_sha256"]):
            raise ValueError("community decision hash invalid")
        if _sha({k: v for k, v in event.items() if k != "decision_sha256"}) != event["decision_sha256"]:
            raise ValueError("community decision checksum mismatch")
        decided.add(ref)
        prev = event["decision_sha256"]
    return {
        "schema": SCHEMA, "submission_count": len(items), "review_count": len(reviews),
        "pending_count": len(items) - len(decided),
        "decision_counts": {name: sum(e["decision"] == name for e in reviews)
                            for name in sorted(DECISIONS)},
        "snapshot_sha256": doc["snapshot_sha256"],
        "source_paths_included": False, "evidence_urls_included": False,
        "voice_or_firmware_bytes_included": False,
        "hashes_are_digital_signatures": False,
        "independent_device_verified": False, "install_authorized": False,
    }


def _output(output, doc):
    dest = Path(output).expanduser().absolute()
    if dest.suffix.lower() != ".json" or dest.exists() or dest.is_symlink():
        raise FileExistsError("output must be a new .json file")
    doc["snapshot_sha256"] = _sha(_sealable(doc))
    encoded = json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False,
                         allow_nan=False).encode("utf-8") + b"\n"
    if len(encoded) > MAX_BYTES:
        raise ValueError("community inbox exceeds 512 KiB")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("xb") as stream:
        try:
            stream.write(encoded)
        except BaseException:
            stream.close()
            dest.unlink(missing_ok=True)
            raise
    return {"output": str(dest), **_audit(doc)}


def init_inbox(output):
    return _output(output, {
        "schema": SCHEMA, "submissions": [], "reviews": [],
        "previous_snapshot_sha256": None, "snapshot_sha256": ZERO_SHA,
        "install_authorized": False, "independent_device_verified": False,
    })


def add_report(inbox, report, output):
    doc = _read(inbox)
    src = Path(report).expanduser()
    if src.is_symlink() or not src.is_file():
        raise ValueError("community report must be a regular local file")
    if src.stat().st_size > 65536:
        raise ValueError("community report exceeds 64 KiB")
    try:
        with src.open("rb") as stream:
            evidence = json.loads(stream.read(65537).decode("utf-8"),
                                  object_pairs_hook=_no_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid community report JSON") from exc
    if not isinstance(evidence, dict) or not isinstance(evidence.get("model_id"), str):
        raise ValueError("report model identity required")
    model_id = evidence["model_id"]
    info = _read_report(src, model_id)
    if len(doc["submissions"]) >= MAX_ITEMS:
        raise ValueError("community inbox submission limit reached")
    if any(e["id"] == info["report_sha256"] for e in doc["submissions"]):
        raise ValueError("duplicate community submission")
    doc["previous_snapshot_sha256"] = doc["snapshot_sha256"]
    doc["submissions"].append({
        "id": info["report_sha256"], "model_id": model_id,
        "firmware": info["firmware"],
        "package_sha256": info["package_sha256"],
        "observed_steps": info["observed_steps"],
        "self_report_status": info["self_report_status"],
        "source_report_sha256": info["report_sha256"],
    })
    return _output(output, doc)


def moderate_report(inbox, submission_id, decision, reviewer, note, output):
    doc = _read(inbox)
    if decision not in DECISIONS:
        raise ValueError("community decision must be research-accepted, needs-evidence or rejected")
    if submission_id not in {s["id"] for s in doc["submissions"]}:
        raise ValueError("unknown submission")
    if any(r["submission_id"] == submission_id for r in doc["reviews"]):
        raise ValueError("submission already reviewed")
    if not _text(reviewer) or not _text(note, size=240):
        raise ValueError("human reviewer and 1..240 printable note required")
    prev = doc["reviews"][-1]["decision_sha256"] if doc["reviews"] else ZERO_SHA
    event = {
        "sequence": len(doc["reviews"]) + 1,
        "submission_id": submission_id,
        "decision": decision, "reviewer": reviewer, "note": note,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "previous_decision_sha256": prev,
    }
    event["decision_sha256"] = _sha(event)
    doc["previous_snapshot_sha256"] = doc["snapshot_sha256"]
    doc["reviews"].append(event)
    return _output(output, doc)


def audit_inbox(path):
    return _audit(_read(path))
