"""Offline reconciliation of untrusted per-firmware hardware claims.

Never grants install permissions, changes transport policy, or contacts robots.
"""
import hashlib
import json
from pathlib import Path

from .catalog import model_by_id
from .community_testkit import _FIRMWARE
from .hardware_acceptance import assess_hardware_acceptance
from .model_discovery import summarize_model
from .translation_overlays import _no_duplicate_keys

SCHEMA = "vvh.firmware-matrix.v1"
LIMIT = 64
MAX_BYTES = 65536


def _read_report(value, expected_model):
    path = Path(value).expanduser()
    if path.is_symlink() or not path.is_file():
        raise ValueError("report must be a regular local file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if not 1 <= len(raw) <= MAX_BYTES:
        raise ValueError("report exceeds 65536 bytes or is empty")
    try:
        report = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid UTF-8 report JSON") from exc
    check = assess_hardware_acceptance(report, expected_model=expected_model)
    firmware = check["firmware"]
    if firmware != firmware.strip() or not _FIRMWARE.fullmatch(firmware):
        raise ValueError("invalid canonical non-sensitive firmware version")
    digest = hashlib.sha256(raw).hexdigest()
    with path.open("rb") as stream:
        if hashlib.sha256(stream.read(MAX_BYTES + 1)).hexdigest() != digest:
            raise ValueError("report changed during validation")
    return {"report_sha256": digest, "firmware": firmware,
            "package_sha256": check["package_sha256"],
            "observed_steps": sorted(check["observed_steps"]),
            "missing_steps": sorted(check["missing_steps"]),
            "self_report_status": check["status"]}


def firmware_matrix(model_id, report_paths):
    model = model_by_id(model_id)
    if model["id"] != model_id:
        raise ValueError("exact canonical model id required (no aliases)")
    if (not isinstance(report_paths, (list, tuple)) or
            not 1 <= len(report_paths) <= LIMIT):
        raise ValueError("1..64 local reports required")
    claims = [_read_report(p, model_id) for p in report_paths]
    if len({r["report_sha256"] for r in claims}) != len(claims):
        raise ValueError("duplicate identical report cannot be counted")
    claims.sort(key=lambda r: (r["firmware"], r["package_sha256"], r["report_sha256"]))
    grouped = {}
    for claim in claims:
        grouped.setdefault(claim["firmware"], []).append(claim)
    firmwares = []
    for fw, entries in sorted(grouped.items()):
        shas = sorted({r["package_sha256"] for r in entries})
        observations = {tuple(r["observed_steps"]) for r in entries}
        firmwares.append({
            "firmware": fw, "report_count": len(entries),
            "package_sha256s": shas, "package_digest_count": len(shas),
            "ready_for_independent_review": sum(
                r["self_report_status"] == "ready-for-independent-hardware-review"
                for r in entries),
            "needs_reconciliation": len(shas) > 1 or len(observations) > 1,
            "independent_acceptances": 0, "install_authorized": False,
        })
    return {
        "schema": SCHEMA, "model_id": model_id, "model_name": model["name"],
        "model_catalog_transport_status": summarize_model(model_id)["custom_install_status"],
        "registry_reports_device_tested": bool(model.get("device_tested")),
        "report_count": len(claims), "firmwares": firmwares, "reports": claims,
        "source_paths_embedded": False, "public_references_embedded": False,
        "source_report_bytes_embedded": False,
        "per_firmware_hardware_verified": False,
        "independent_review_performed": False,
        "registry_mutated": False, "transport_policy_changed": False,
        "install_authorized": False,
        "note": "Untrusted firmware self-reports, never an automatic install or signing authorization.",
    }
