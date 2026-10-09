"""Evidence-only per-firmware custom voice acceptance checklist.

Does not change model registry, transport policy, token, firmware or device.
Self-reported steps never establish manufacturer signing or safe installation.
"""
import json
import re
from pathlib import Path

from .catalog import model_by_id
from .transport_evidence import _check_no_secrets, EvidenceError

SCHEMA = "vvh.hardware-acceptance.v1"
MAX_BYTES = 64 * 1024
DIGEST = re.compile(r"^[0-9a-f]{64}$")
URL = re.compile(r"^https://[^/\s@]+/[^\s]*$")
FIELDS = (
    "package_signature_reviewed",
    "device_download_observed",
    "device_playback_heard",
    "reboot_persistence_checked",
    "stock_rollback_tested",
)


def assess_hardware_acceptance(record, expected_model=None):
    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        raise EvidenceError("invalid hardware-acceptance schema")
    _check_no_secrets(record)
    model = record.get("model_id")
    if not isinstance(model, str) or (expected_model and model != expected_model):
        raise EvidenceError("hardware evidence model mismatch")
    canonical = model_by_id(model)
    if canonical["id"] != model:
        raise EvidenceError("hardware evidence requires exact canonical model ID")
    firmware = record.get("firmware")
    if not isinstance(firmware, str) or not 1 <= len(firmware.strip()) <= 128:
        raise EvidenceError("specific firmware string required")
    package = record.get("package")
    if not isinstance(package, dict) or not isinstance(package.get("sha256"), str) or not DIGEST.fullmatch(package["sha256"]):
        raise EvidenceError("actual candidate package sha256 required")
    if type(package.get("size_bytes")) is not int or not 1 <= package["size_bytes"] <= 1_000_000_000:
        raise EvidenceError("invalid candidate package size")
    evidence = record.get("observations")
    if not isinstance(evidence, dict) or set(evidence) != set(FIELDS):
        raise EvidenceError("all five observation fields are required")
    for step, value in evidence.items():
        if not isinstance(value, dict) or type(value.get("observed")) is not bool:
            raise EvidenceError(f"{step}: explicit boolean observation required")
        ref = value.get("reference")
        if value["observed"] and (not isinstance(ref, str) or
                                  not URL.fullmatch(ref) or len(ref) > 2048):
            raise EvidenceError(f"{step}: evidence link required")
        if ref is not None and (not isinstance(ref, str) or len(ref) > 2048):
            raise EvidenceError(f"{step}: invalid reference")
    claims = [field for field in FIELDS if evidence[field]["observed"]]
    return {
        "schema": "vvh.hardware-acceptance-assessment.v1",
        "model_id": model, "firmware": firmware,
        "package_sha256": package["sha256"],
        "observed_steps": claims,
        "missing_steps": [field for field in FIELDS if field not in claims],
        "status": "ready-for-independent-hardware-review" if len(claims) == len(FIELDS)
                  else "incomplete-research-only",
        "registry_mutated": False,
        "transport_policy_changed": False,
        "manufacturer_signature_automatically_verified": False,
        "evidence_independently_verified": False,
        "install_authorized": False,
    }


def inspect_acceptance_file(path, expected_model=None):
    path = Path(path).expanduser()
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise EvidenceError("hardware acceptance file missing or too large")
    try:
        data = json.loads(path.read_text("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as e:
        raise EvidenceError("invalid hardware acceptance JSON") from e
    return assess_hardware_acceptance(data, expected_model=expected_model)
