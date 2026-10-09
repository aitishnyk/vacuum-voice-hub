"""Offline evidence bundle: check hashes, never ship firmware or robot credentials.

The sources are self-reported and explicitly NOT independent hardware proof.
"""
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from .hardware_acceptance import (
    SCHEMA as ACCEPTANCE_SCHEMA, assess_hardware_acceptance, MAX_BYTES,
)
from .transport_evidence import EvidenceError

SCHEMA = "vvh.firmware-evidence-bundle.v1"
MAX_ZIP = 128 * 1024
MAX_MEMBER = 64 * 1024


def _json_no_duplicates(data):
    def pairs(entries):
        out = {}
        for key, value in entries:
            if key in out:
                raise ValueError("duplicate evidence JSON key")
            out[key] = value
        return out
    return json.loads(data.decode("utf-8"), object_pairs_hook=pairs)


def _evidence(path, package_path):
    src = Path(path).expanduser().resolve(strict=True)
    if not src.is_file() or not 0 < src.stat().st_size <= MAX_BYTES:
        raise ValueError("hardware report must be 1..64 KiB")
    try:
        record = _json_no_duplicates(src.read_bytes())
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid hardware JSON") from exc
    assessment = assess_hardware_acceptance(record)
    candidate = Path(package_path).expanduser().resolve(strict=True)
    if not candidate.is_file() or not 0 < candidate.stat().st_size <= 1_000_000_000:
        raise ValueError("candidate package missing or too large")
    sha = hashlib.sha256()
    length = 0
    with candidate.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            length += len(chunk)
            sha.update(chunk)
    if sha.hexdigest() != record["package"]["sha256"] or length != record["package"]["size_bytes"]:
        raise ValueError("actual local candidate package fingerprint does not match evidence")
    return record, assessment, candidate


def create_evidence_bundle(report_path, candidate_package, output):
    record, assessed, package = _evidence(report_path, candidate_package)
    manifest = {
        "schema": SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_id": assessed["model_id"], "firmware": assessed["firmware"],
        "candidate_package_sha256": assessed["package_sha256"],
        "candidate_package_size_bytes": record["package"]["size_bytes"],
        "candidate_package_included": False,
        "observed_steps": assessed["observed_steps"],
        "missing_steps": assessed["missing_steps"],
        "independently_verified": False,
        "install_authorized": False,
    }
    dest = Path(output).expanduser().absolute()
    if dest.suffix.lower() != ".zip":
        raise ValueError("evidence output must be .zip")
    if dest.resolve() == package or dest.resolve() == Path(report_path).expanduser().resolve():
        raise ValueError("evidence cannot overwrite its inputs")
    dest.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with dest.open("xb") as target:
            created = True
            with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr("evidence.json", json.dumps(record, ensure_ascii=False,
                                                        sort_keys=True, indent=2) + "\n")
                z.writestr("assessment.json", json.dumps(assessed, ensure_ascii=False,
                                                          sort_keys=True, indent=2) + "\n")
                z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False,
                                                        sort_keys=True, indent=2) + "\n")
        return {"schema": SCHEMA, "file": str(dest),
                "bytes": dest.stat().st_size,
                "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
                "model_id": assessed["model_id"], "firmware": assessed["firmware"],
                "candidate_package_included": False, "install_authorized": False}
    except BaseException:
        if created:
            dest.unlink(missing_ok=True)
        raise


def verify_evidence_bundle(path, candidate_package, *, expected_model=None):
    src = Path(path).expanduser().resolve(strict=True)
    if not src.is_file() or not 0 < src.stat().st_size <= MAX_ZIP:
        raise ValueError("evidence ZIP missing or exceeds 128 KiB")
    with zipfile.ZipFile(src) as archive:
        entries = archive.infolist()
        if sorted(x.filename for x in entries) != [
            "assessment.json", "evidence.json", "manifest.json"]:
            raise ValueError("unexpected evidence ZIP entries")
        if len(entries) != 3:
            raise ValueError("duplicate evidence ZIP member")
        for member in entries:
            if member.flag_bits & 1 or member.file_size > MAX_MEMBER:
                raise ValueError("encrypted or oversized evidence ZIP entry")
        manifest = _json_no_duplicates(archive.read("manifest.json"))
        record = _json_no_duplicates(archive.read("evidence.json"))
        assessment = _json_no_duplicates(archive.read("assessment.json"))
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise ValueError("invalid evidence bundle manifest")
    if manifest.get("candidate_package_included") is not False:
        raise ValueError("package inclusion must be false")
    actual = assess_hardware_acceptance(record, expected_model=expected_model)
    if actual != assessment:
        raise ValueError("evidence assessment was modified")
    if (manifest.get("model_id") != actual["model_id"] or
        manifest.get("firmware") != actual["firmware"] or
        manifest.get("candidate_package_sha256") != actual["package_sha256"] or
        manifest.get("candidate_package_size_bytes") != record["package"]["size_bytes"] or
        manifest.get("observed_steps") != actual["observed_steps"] or
        manifest.get("missing_steps") != actual["missing_steps"] or
        manifest.get("install_authorized") is not False or
        manifest.get("independently_verified") is not False):
        raise ValueError("evidence manifest differs from checked hardware report")
    package = Path(candidate_package).expanduser().resolve(strict=True)
    size = 0
    hasher = hashlib.sha256()
    if not package.is_file() or package.stat().st_size > 1_000_000_000:
        raise ValueError("local candidate package missing or oversized")
    with package.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            size += len(chunk)
            hasher.update(chunk)
    if size != record["package"]["size_bytes"] or hasher.hexdigest() != actual["package_sha256"]:
        raise ValueError("candidate package changed since hardware evidence creation")
    return {
        "schema": SCHEMA, "valid": True, "model_id": actual["model_id"],
        "firmware": actual["firmware"],
        "candidate_package_sha256": hasher.hexdigest(),
        "hardware_report_status": actual["status"],
        "self_reported_claims_only": True,
        "independently_verified": False,
        "install_authorized": False,
    }
