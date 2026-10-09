"""Offline signed whole-voicepack manifest bound to an exact Creator review.

A valid signature proves possession of a supplied Ed25519 key. It does NOT
authorize installation, prove an audio license or certify a speaker's language.
"""
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .production_review import audit_review, _load_json, _snapshot, _hash
from .review_history import audit_review_history
from .reviewer_attestation import _crypto, _canonical, _read_key

SCHEMA = "vvh.signed-pack-manifest.v1"
MAX_SIGNED_BYTES = 512 * 1024


def _whole_pack_payload(review_path, *, overlay_path=None):
    result = audit_review(review_path, overlay_path=overlay_path)
    if not result["valid"]:
        raise ValueError("pack source review is invalid or stale")
    audit_review_history(review_path)
    review = _load_json(review_path)
    root = Path(review["workspace"]).resolve()
    # audit_review rehashed all current recordings and task mappings.
    rows = []
    for row in review["tasks"]:
        audio = row["audio"]
        if not audio:
            continue
        state = row["review"]
        rows.append({
            "semantic": row["semantic"], "event_ids": row["event_ids"],
            "audio_file": audio["file"], "audio_sha256": audio["sha256"],
            "audio_bytes": audio["bytes"], "text": row["text"],
            "human_review_status": state["status"],
            "human_reviewer_claim": state["reviewer"],
            "human_reviewed_at": state["reviewed_at"],
            "human_language_attested": state["language_attested"] is True,
            "human_rights_attested": state["rights_attested"] is True,
        })
    rows.sort(key=lambda x: x["semantic"])
    if not rows:
        raise ValueError("cannot sign empty voice pack without assigned audio")
    return {
        "schema": SCHEMA,
        "model_id": review["model_id"], "pack_id": review["pack_id"],
        "locale": review["locale"],
        "workspace_manifest_sha256": review["workspace_manifest_sha256"],
        "text_script_digest": review["text_script_digest"],
        "audio_count": len(rows),
        "approved_count": sum(x["human_review_status"] == "approved" for x in rows),
        "all_recordings_human_approved": all(
            x["human_review_status"] == "approved" for x in rows),
        "recordings": rows,
        "install_authorized": False,
        "rights_independently_verified": False,
        "spoken_language_automatically_verified": False,
    }


def _private(path):
    serialization, Ed25519PrivateKey, _, _ = _crypto()
    key = serialization.load_pem_private_key(_read_key(path), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("only Ed25519 PEM private keys supported")
    return serialization, key


def _read_signed(path):
    p = Path(path).expanduser().resolve(strict=True)
    if not p.is_file() or not 0 < p.stat().st_size <= MAX_SIGNED_BYTES:
        raise ValueError("signed whole-pack manifest missing or larger than 512 KiB")
    def no_duplicates(pairs):
        data = {}
        for key, val in pairs:
            if key in data:
                raise ValueError("duplicate signed pack JSON key")
            data[key] = val
        return data
    try:
        obj = json.loads(p.read_text("utf-8"), object_pairs_hook=no_duplicates)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid signed pack JSON") from exc
    if not isinstance(obj, dict) or obj.get("schema") != SCHEMA or obj.get("algorithm") != "Ed25519":
        raise ValueError("unsupported signed pack format")
    return obj


def sign_pack(review_path, private_key_path, output, *,
              require_approved=False, overlay_path=None):
    payload = _whole_pack_payload(review_path, overlay_path=overlay_path)
    if require_approved and not payload["all_recordings_human_approved"]:
        raise ValueError("all assigned recordings must have explicit human approval")
    serialization, key = _private(private_key_path)
    public = key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    payload["signed_at"] = datetime.now(timezone.utc).isoformat()
    signed = {
        "schema": SCHEMA, "algorithm": "Ed25519",
        "public_key_sha256": hashlib.sha256(public).hexdigest(),
        "payload": payload,
        "signature": base64.b64encode(key.sign(_canonical(payload))).decode("ascii"),
        "private_key_included": False, "install_authorized": False,
    }
    dest = Path(output).expanduser().absolute()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("x", encoding="utf-8") as out:
        json.dump(signed, out, ensure_ascii=False, sort_keys=True, indent=2)
        out.write("\n")
    return {
        "schema": SCHEMA, "file": str(dest),
        "model_id": payload["model_id"], "audio_count": payload["audio_count"],
        "approved_count": payload["approved_count"],
        "all_recordings_human_approved": payload["all_recordings_human_approved"],
        "public_key_sha256": signed["public_key_sha256"],
        "install_authorized": False,
    }


def verify_pack(signed_path, public_key_path, review_path, *, overlay_path=None):
    serialization, _, Ed25519PublicKey, InvalidSignature = _crypto()
    signed = _read_signed(signed_path)
    public = serialization.load_pem_public_key(_read_key(public_key_path))
    if not isinstance(public, Ed25519PublicKey):
        raise ValueError("only Ed25519 PEM public keys supported")
    raw = public.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    fingerprint = hashlib.sha256(raw).hexdigest()
    if fingerprint != signed.get("public_key_sha256"):
        raise ValueError("Ed25519 public key fingerprint mismatch")
    payload = signed.get("payload")
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError("invalid pack signing payload")
    try:
        signature = base64.b64decode(signed["signature"], validate=True)
    except (KeyError, ValueError) as exc:
        raise ValueError("invalid pack signature encoding") from exc
    if len(signature) != 64:
        raise ValueError("invalid pack signature length")
    try:
        public.verify(signature, _canonical(payload))
    except InvalidSignature as exc:
        raise ValueError("whole-pack Ed25519 signature invalid") from exc
    signed_at = payload.get("signed_at")
    if not isinstance(signed_at, str) or not 1 <= len(signed_at) <= 64:
        raise ValueError("signed timestamp missing")
    fresh = _whole_pack_payload(review_path, overlay_path=overlay_path)
    if {k: v for k, v in payload.items() if k != "signed_at"} != fresh:
        raise ValueError("whole-pack signature is stale: source audio, mapping or human review changed")
    return {
        "schema": SCHEMA, "signature_valid": True,
        "current_source_matches": True,
        "model_id": payload["model_id"],
        "audio_count": payload["audio_count"], "approved_count": payload["approved_count"],
        "public_key_sha256": fingerprint,
        "signer_identity_independently_verified": False,
        "voice_rights_independently_verified": False,
        "manufacturer_install_authorized": False,
        "install_authorized": False,
    }
