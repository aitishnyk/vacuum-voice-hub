"""Create metadata-only, local hardware-test checklists for volunteers.

This never contacts a robot, performs authentication, includes audio/firmware
bytes in the report, or modifies a model's installation policy.
"""
import hashlib
import json
import os
import re
import stat
from pathlib import Path

from .catalog import model_by_id
from .hardware_acceptance import FIELDS, SCHEMA, assess_hardware_acceptance
from .transport_evidence import EvidenceError

MAX_PACKAGE_BYTES = 1_000_000_000
_FIRMWARE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+() -]{0,127}$")


def create_hardware_scaffold(model_id, firmware, package, output):
    """Hash one real local package and write an exclusive, unapproved checklist.

    Local paths and source binary bytes are intentionally absent from the JSON.
    Every device-facing observation begins as false, not a claimed test.
    """
    if not isinstance(model_id, str):
        raise EvidenceError("canonical model ID required")
    model = model_by_id(model_id)
    if model["id"] != model_id:
        raise EvidenceError("exact canonical model ID required (aliases are not evidence)")
    if (not isinstance(firmware, str) or firmware != firmware.strip()
            or not _FIRMWARE.fullmatch(firmware)):
        raise EvidenceError("firmware must be 1..128 non-sensitive version characters")
    src = Path(package).expanduser().absolute()
    dst = Path(output).expanduser().absolute()
    if dst.suffix.lower() != ".json" or dst.resolve() == src.resolve():
        raise EvidenceError("output must be a separate .json file")
    if dst.exists() or dst.is_symlink():
        raise FileExistsError(f"report already exists: {dst}")
    if src.is_symlink():
        raise EvidenceError("symlinked package source refused")
    try:
        # stat on the open descriptor limits file-swap and non-regular-file risks.
        with src.open("rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or not 1 <= before.st_size <= MAX_PACKAGE_BYTES:
                raise EvidenceError("candidate must be a regular file of 1..1,000,000,000 bytes")
            digest = hashlib.sha256()
            total = 0
            while True:
                block = stream.read(256 * 1024)
                if not block:
                    break
                total += len(block)
                if total > MAX_PACKAGE_BYTES:
                    raise EvidenceError("candidate package exceeds 1,000,000,000 bytes")
                digest.update(block)
            after = os.fstat(stream.fileno())
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (
                    after.st_size, after.st_mtime_ns, after.st_ino) or total != before.st_size:
                raise EvidenceError("candidate file changed during hashing")
    except (IsADirectoryError, FileNotFoundError) as exc:
        raise EvidenceError("regular local candidate package required") from exc
    record = {
        "schema": SCHEMA,
        "model_id": model_id,
        "firmware": firmware,
        "package": {"sha256": digest.hexdigest(), "size_bytes": total},
        "observations": {
            item: {"observed": False, "reference": None} for item in FIELDS
        },
    }
    assessed = assess_hardware_acceptance(record, expected_model=model_id)
    if assessed["status"] != "incomplete-research-only" or assessed["install_authorized"]:
        raise EvidenceError("draft report unexpectedly claims hardware acceptance")
    dst.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    # Exclusive output also guards concurrent invocations. Failed partial writes
    # are cleaned up, never leaving a misleading valid-looking test report.
    with dst.open("x", encoding="utf-8") as stream:
        try:
            stream.write(payload)
        except BaseException:
            stream.close()
            dst.unlink(missing_ok=True)
            raise
    return {
        "schema": "vvh.community-test-scaffold-result.v1",
        "output": str(dst),
        "model_id": model_id,
        "package_sha256": digest.hexdigest(),
        "package_size_bytes": total,
        "assessment": assessed,
        "report_contains_package_bytes": False,
        "observation_count": len(FIELDS),
        "all_observations_unverified": True,
        "install_authorized": False,
        "registry_mutated": False,
        "next_step": "Fill only witnessed observations with public HTTPS evidence links; run 'vvh research hardware-acceptance' before sharing.",
    }
