"""Detached, metadata-only human moderation of community hardware reports.

Verifying a signature proves possession of a supplied key, never device
functionality, a real-world reviewer identity or authorization to install.
"""
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .firmware_matrix import _read_report
from .reviewer_attestation import _crypto, _canonical, _read_key
from .signed_pack import _private
from .translation_overlays import _no_duplicate_keys

SCHEMA = "vvh.community-moderation.v1"
DECISIONS = ("needs-evidence", "rejected-as-insufficient", "accept-for-manual-review")
MAX_BYTES = 32768


def _reviewer(value):
    return (isinstance(value, str) and 1 <= len(value) <= 128 and
            value.strip() == value and
            not any(ord(c) < 32 or ord(c) == 127 for c in value))


def _snapshot(report_path, model_id):
    record = _read_report(report_path, model_id)
    return {
        "model_id": model_id, "firmware": record["firmware"],
        "source_report_sha256": record["report_sha256"],
        "package_sha256": record["package_sha256"],
        "observed_steps": record["observed_steps"],
        "missing_steps": record["missing_steps"],
        "source_self_report_status": record["self_report_status"],
    }


def sign_moderation(report_path, model_id, reviewer, decision, private_key, output):
    if not _reviewer(reviewer):
        raise ValueError("attributed moderator identity required")
    if decision not in DECISIONS:
        raise ValueError("unsupported moderation decision")
    evidence = _snapshot(report_path, model_id)
    if decision == "accept-for-manual-review" and evidence["missing_steps"]:
        raise ValueError("cannot shortlist incomplete self-reported evidence")
    serialization, key = _private(private_key)
    key_raw = key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    payload = {
        "schema": SCHEMA, **evidence, "reviewer_claim": reviewer,
        "decision": decision, "signed_at": datetime.now(timezone.utc).isoformat(),
        "independent_on_device_test_performed": False,
        "hardware_install_authorized": False,
    }
    doc = {
        "schema": SCHEMA, "algorithm": "Ed25519",
        "public_key_sha256": hashlib.sha256(key_raw).hexdigest(),
        "payload": payload,
        "signature": base64.b64encode(key.sign(_canonical(payload))).decode("ascii"),
        "private_key_included": False, "install_authorized": False,
    }
    destination = Path(output).expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("signed moderation output already exists")
    bytes_out = (json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if len(bytes_out) > MAX_BYTES:
        raise ValueError("moderation document exceeds 32 KiB")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as file:
        try:
            file.write(bytes_out)
        except BaseException:
            file.close()
            destination.unlink(missing_ok=True)
            raise
    return {
        "schema": SCHEMA, "file": str(destination),
        "decision": decision, "model_id": model_id,
        "public_key_sha256": doc["public_key_sha256"],
        "source_report_sha256": evidence["source_report_sha256"],
        "physical_test_verified": False, "install_authorized": False,
    }


def verify_moderation(signed_path, report_path, model_id, public_key):
    source = Path(signed_path).expanduser()
    if source.is_symlink() or not source.is_file():
        raise ValueError("signed moderation must be a regular file")
    with source.open("rb") as file:
        raw = file.read(MAX_BYTES + 1)
    if not 1 <= len(raw) <= MAX_BYTES:
        raise ValueError("signed moderation exceeds 32 KiB")
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid signed moderation JSON") from exc
    if (not isinstance(doc, dict) or doc.get("schema") != SCHEMA or
            doc.get("algorithm") != "Ed25519" or doc.get("install_authorized") is not False):
        raise ValueError("unsupported signed moderation schema or unsafe authorization")
    serialization, _, Ed25519PublicKey, InvalidSignature = _crypto()
    key = serialization.load_pem_public_key(_read_key(public_key))
    if not isinstance(key, Ed25519PublicKey):
        raise ValueError("Ed25519 public key required")
    public_raw = key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    fingerprint = hashlib.sha256(public_raw).hexdigest()
    if doc.get("public_key_sha256") != fingerprint:
        raise ValueError("moderator public key fingerprint mismatch")
    payload = doc.get("payload")
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError("signed moderation payload missing")
    if (payload.get("decision") not in DECISIONS or
            not _reviewer(payload.get("reviewer_claim")) or
            payload.get("hardware_install_authorized") is not False or
            payload.get("independent_on_device_test_performed") is not False):
        raise ValueError("unsafe or invalid moderation claim")
    when = payload.get("signed_at")
    if not isinstance(when, str) or len(when) > 64 or not when.endswith("+00:00"):
        raise ValueError("invalid moderation timestamp")
    try:
        signature = base64.b64decode(doc["signature"], validate=True)
    except (ValueError, KeyError) as exc:
        raise ValueError("invalid moderation signature encoding") from exc
    if len(signature) != 64:
        raise ValueError("invalid moderation signature size")
    try:
        key.verify(signature, _canonical(payload))
    except InvalidSignature as exc:
        raise ValueError("invalid Ed25519 moderation signature") from exc
    fresh = _snapshot(report_path, model_id)
    if any(payload.get(name) != value for name, value in fresh.items()):
        raise ValueError("signed moderation is stale: source report or model changed")
    if payload["decision"] == "accept-for-manual-review" and fresh["missing_steps"]:
        raise ValueError("review shortlist lacks all self-reported steps")
    return {
        "schema": SCHEMA, "signature_valid": True, "source_snapshot_matches": True,
        "decision": payload["decision"], "model_id": model_id,
        "firmware": fresh["firmware"], "public_key_sha256": fingerprint,
        "signer_identity_independently_verified": False,
        "physical_device_claims_independently_verified": False,
        "manufacturer_approval_verified": False,
        "install_authorized": False,
    }
