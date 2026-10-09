"""Optional Ed25519 detached attestations of a human review, offline.

Signatures authenticate possession of a user-provided key, NOT the reviewer's
real-world identity, legal distribution rights, native-language accuracy, or
manufacturer permission to upload a custom robot voice.
"""
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .production_review import _load_json, audit_review
from .review_history import audit_review_history

SCHEMA = "vvh.reviewer-attestation.v1"
MAX_KEY_BYTES = 16384
MAX_ATTESTATION_BYTES = 16384


def _crypto():
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey, Ed25519PublicKey,
        )
        from cryptography.exceptions import InvalidSignature
    except ImportError as exc:
        raise RuntimeError("Install optional reviewer signing support: pip install 'vacuum-voice-hub[review-signing]'") from exc
    return serialization, Ed25519PrivateKey, Ed25519PublicKey, InvalidSignature


def _read_key(path):
    p = Path(path).expanduser().resolve(strict=True)
    if not p.is_file() or not 0 < p.stat().st_size <= MAX_KEY_BYTES:
        raise ValueError("PEM key must be a local file of up to 16 KiB")
    return p.read_bytes()


def _canonical(payload):
    return json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _payload(review_path, semantic, *, overlay_path=None):
    report = audit_review(review_path, overlay_path=overlay_path)
    if not report["valid"]:
        raise ValueError("cannot attest to a stale or invalid Creator review")
    audit_review_history(review_path)
    record = _load_json(review_path)
    row = next((x for x in record["tasks"] if x["semantic"] == semantic), None)
    if not row or not row.get("audio"):
        raise ValueError("a currently assigned audio recording is required")
    review = row["review"]
    if (review["status"] != "approved" or review.get("language_attested") is not True
            or review.get("rights_attested") is not True or not review.get("reviewer")):
        raise ValueError("signed attestation requires an explicit approved human review")
    return {
        "schema": SCHEMA,
        "model_id": record["model_id"], "pack_id": record["pack_id"],
        "locale": record["locale"], "semantic": semantic,
        "event_ids": row["event_ids"],
        "audio_sha256": row["audio"]["sha256"],
        "audio_bytes": row["audio"]["bytes"],
        "text_script_digest": record["text_script_digest"],
        "workspace_manifest_sha256": record["workspace_manifest_sha256"],
        "reviewer_claim": review["reviewer"],
        "reviewed_at": review["reviewed_at"],
        "language_attested": True, "rights_attested": True,
        "review_status": "approved",
    }


def sign_review(review_path, semantic, private_key_path, output, *, overlay_path=None):
    serialization, Ed25519PrivateKey, _, _ = _crypto()
    private = serialization.load_pem_private_key(_read_key(private_key_path), password=None)
    if not isinstance(private, Ed25519PrivateKey):
        raise ValueError("only Ed25519 PEM private keys are supported")
    public_raw = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    payload = _payload(review_path, semantic, overlay_path=overlay_path)
    payload["signed_at"] = datetime.now(timezone.utc).isoformat()
    signed = {
        "schema": SCHEMA, "algorithm": "Ed25519",
        "public_key_sha256": hashlib.sha256(public_raw).hexdigest(),
        "payload": payload,
        "signature": base64.b64encode(private.sign(_canonical(payload))).decode("ascii"),
        "identity_independently_verified": False,
        "rights_independently_verified": False,
        "install_authorized": False,
    }
    destination = Path(output).expanduser().absolute()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(signed, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")
    return {"schema": SCHEMA, "file": str(destination),
            "public_key_sha256": signed["public_key_sha256"],
            "model_id": payload["model_id"], "semantic": semantic,
            "signature_created": True, "install_authorized": False}


def verify_attestation(attestation_path, public_key_path, review_path, *,
                       overlay_path=None):
    serialization, _, Ed25519PublicKey, InvalidSignature = _crypto()
    path = Path(attestation_path).expanduser().resolve(strict=True)
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_ATTESTATION_BYTES:
        raise ValueError("signed attestation must be 1..16384 bytes")
    def reject_duplicates(pairs):
        output = {}
        for key, value in pairs:
            if key in output:
                raise ValueError("duplicate signed attestation JSON field")
            output[key] = value
        return output
    data = json.loads(path.read_text("utf-8"), object_pairs_hook=reject_duplicates)
    if not isinstance(data, dict) or data.get("schema") != SCHEMA or data.get("algorithm") != "Ed25519":
        raise ValueError("unsupported reviewer attestation")
    public = serialization.load_pem_public_key(_read_key(public_key_path))
    if not isinstance(public, Ed25519PublicKey):
        raise ValueError("only Ed25519 PEM public keys are supported")
    raw = public.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    fingerprint = hashlib.sha256(raw).hexdigest()
    if fingerprint != data.get("public_key_sha256"):
        raise ValueError("public signing key fingerprint mismatch")
    payload = data.get("payload")
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError("invalid signed payload")
    try:
        signature = base64.b64decode(data["signature"], validate=True)
    except (ValueError, KeyError) as exc:
        raise ValueError("invalid detached signature") from exc
    if len(signature) != 64:
        raise ValueError("invalid Ed25519 signature size")
    try:
        public.verify(signature, _canonical(payload))
    except InvalidSignature as exc:
        raise ValueError("Ed25519 signature verification failed") from exc
    signed_at = payload.get("signed_at")
    if not isinstance(signed_at, str) or len(signed_at) > 64:
        raise ValueError("invalid signed timestamp")
    fresh = _payload(review_path, payload.get("semantic"), overlay_path=overlay_path)
    if {k: v for k, v in payload.items() if k != "signed_at"} != fresh:
        raise ValueError("signed audio, script, review or model no longer matches")
    return {
        "schema": SCHEMA, "signature_valid": True,
        "source_snapshot_matches": True,
        "public_key_sha256": fingerprint, "model_id": payload["model_id"],
        "semantic": payload["semantic"],
        "signer_identity_independently_verified": False,
        "copyright_rights_independently_verified": False,
        "spoken_language_verified": False, "install_authorized": False,
    }
