"""Offline review of proposed voice-package transport evidence.

No network calls, robot actions, credential storage or model-registry mutations.
This is a research intake gate, NOT an installation authorization mechanism.
"""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = "vvh.transport-evidence.v1"
MAX_BYTES = 64 * 1024
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_MODEL = re.compile(r"[a-z0-9]+(?:[._-][a-z0-9]+)+\Z")
_STAGES = {"package_inspected", "request_observed", "device_downloaded",
           "device_reported_success"}
_FORBIDDEN_KEYS = {"token", "password", "secret", "api_key", "auth", "authorization",
                   "credential", "cookie", "ip", "ip_address", "mac", "mac_address",
                   "device_token", "access_token", "refresh_token", "private_key"}


class EvidenceError(ValueError):
    """Invalid, incomplete, or potentially sensitive research evidence."""


def _check_no_secrets(value):
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in _FORBIDDEN_KEYS or normalized.endswith("_token"):
                raise EvidenceError(f"sensitive field not permitted: {key}")
            _check_no_secrets(child)
    elif isinstance(value, list):
        for child in value:
            _check_no_secrets(child)


def validate_evidence(record, expected_model=None):
    """Return an evidence assessment; never return an install-policy decision."""
    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        raise EvidenceError("unsupported evidence schema")
    _check_no_secrets(record)
    model = record.get("model_id")
    if not isinstance(model, str) or not _MODEL.fullmatch(model):
        raise EvidenceError("invalid model_id")
    if expected_model is not None and model != expected_model:
        raise EvidenceError("model_id mismatch")
    source = record.get("source")
    if not isinstance(source, str) or len(source) > 2048:
        raise EvidenceError("source must be a public HTTPS URL")
    parsed = urlsplit(source)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.fragment):
        raise EvidenceError("source must be a public HTTPS URL without credentials or fragment")
    package = record.get("package")
    if not isinstance(package, dict):
        raise EvidenceError("package metadata required")
    digest = package.get("sha256")
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        raise EvidenceError("package.sha256 must be 64 lowercase hex characters")
    if type(package.get("size_bytes")) is not int or not (1 <= package["size_bytes"] <= 1_000_000_000):
        raise EvidenceError("invalid package.size_bytes")
    if package.get("format") not in ("tar.gz", "pkg", "zip", "ogg", "mp3", "unknown"):
        raise EvidenceError("invalid package.format")
    stages = record.get("observations")
    if not isinstance(stages, list) or not stages or len(stages) > len(_STAGES):
        raise EvidenceError("observations must be a bounded list")
    if any(not isinstance(stage, str) or stage not in _STAGES for stage in stages):
        raise EvidenceError("unknown observation stage")
    if len(stages) != len(set(stages)):
        raise EvidenceError("duplicate observation stages")
    hardware = record.get("hardware")
    if hardware is not None:
        if not isinstance(hardware, dict) or not isinstance(hardware.get("firmware"), str) or not hardware["firmware"].strip():
            raise EvidenceError("hardware.firmware required when hardware is supplied")
        if len(hardware["firmware"]) > 128:
            raise EvidenceError("firmware value too long")
    # Observation labels alone never prove on-device package acceptance.
    # This gate only classifies what is reported, without trusting or executing it.
    claimed_success = "device_reported_success" in stages
    needs_review = claimed_success and hardware is not None and "device_downloaded" in stages
    return {
        "schema": "vvh.transport-evidence-assessment.v1",
        "model_id": model,
        "status": "hardware-review-required" if needs_review else "research-only",
        "install_authorized": False,
        "registry_mutated": False,
        "package_sha256": digest,
        "package_size_bytes": package["size_bytes"],
        "package_format": package["format"],
        "observations": sorted(stages),
    }


def inspect_file(path, expected_model=None):
    """Read one bounded UTF-8 JSON research report from disk."""
    path = Path(path)
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise EvidenceError("report exceeds 64 KiB")
    try:
        record = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("invalid UTF-8 JSON report") from exc
    return validate_evidence(record, expected_model=expected_model)
