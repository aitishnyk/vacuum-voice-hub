"""Community test scaffold is local, non-installing and never claims success."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from vacuum_voice_hub.community_testkit import create_hardware_scaffold
from vacuum_voice_hub.hardware_acceptance import (
    FIELDS, inspect_acceptance_file, assess_hardware_acceptance
)
from vacuum_voice_hub.transport_evidence import EvidenceError


def test_scaffold_is_metadata_only_unapproved_and_matches_actual_package(tmp_path):
    package = tmp_path / "original.pkg"
    raw = b"fake developer research candidate " * 128
    package.write_bytes(raw)
    report = tmp_path / "draft.json"
    result = create_hardware_scaffold(
        "roborock.vacuum.a75", "v1.2.3-test", package, report)
    assert result["schema"] == "vvh.community-test-scaffold-result.v1"
    assert result["report_contains_package_bytes"] is False
    assert result["all_observations_unverified"] is True
    assert not result["install_authorized"]
    assert not result["registry_mutated"]
    data = json.loads(report.read_text("utf-8"))
    assert data["model_id"] == "roborock.vacuum.a75"
    assert data["package"]["sha256"] == hashlib.sha256(raw).hexdigest()
    assert data["package"]["size_bytes"] == len(raw)
    assert set(data["observations"]) == set(FIELDS)
    assert all(item == {"observed": False, "reference": None}
               for item in data["observations"].values())
    assert str(package) not in report.read_text()
    assert "fake developer research" not in report.read_text()
    assert inspect_acceptance_file(report)["status"] == "incomplete-research-only"
    assert package.read_bytes() == raw


def test_cannot_replace_an_existing_report_or_own_candidate(tmp_path):
    package = tmp_path / "original.pkg"
    package.write_bytes(b"candidate")
    existing = tmp_path / "existing.json"
    existing.write_bytes(b"DO NOT REPLACE")
    with pytest.raises(FileExistsError):
        create_hardware_scaffold("roborock.vacuum.a75", "1.2.3", package, existing)
    assert existing.read_bytes() == b"DO NOT REPLACE"
    package_json = tmp_path / "candidate.json"
    package_json.write_bytes(b"candidate")
    with pytest.raises(EvidenceError, match="separate"):
        create_hardware_scaffold("roborock.vacuum.a75", "1.2.3", package_json,
                                 package_json)


@pytest.mark.parametrize("firmware", [
    "", "  ", "v1/2", "https://example.org/firmware", "test@foo.com",
    "abc\nPRIVATE", "x" * 129, " v1", "1.2 ",
])
def test_reject_sensitive_ambiguous_firmware_values(tmp_path, firmware):
    source = tmp_path / "candidate.pkg"
    source.write_bytes(b"candidate")
    with pytest.raises(EvidenceError, match="firmware"):
        create_hardware_scaffold("roborock.vacuum.a75", firmware, source,
                                 tmp_path / "report.json")
    assert not (tmp_path / "report.json").exists()


def test_unsupported_model_alias_and_symlink_fail_closed(tmp_path):
    p = tmp_path / "original.pkg"; p.write_bytes(b"candidate")
    with pytest.raises(KeyError):
        create_hardware_scaffold("not.a.real.model", "1.2.3", p, tmp_path / "out.json")
    link = tmp_path / "link.pkg"
    link.symlink_to(p)
    with pytest.raises(EvidenceError, match="symlink"):
        create_hardware_scaffold("roborock.vacuum.a75", "1.2.3", link, tmp_path / "out.json")
    assert not (tmp_path / "out.json").exists()


def test_oversize_or_empty_candidate_rejected_before_report(tmp_path):
    empty = tmp_path / "empty.pkg"
    empty.write_bytes(b"")
    with pytest.raises(EvidenceError, match="1\\.\\.1,000"):
        create_hardware_scaffold("roborock.vacuum.a75", "1.2.3",
                                 empty, tmp_path / "empty.json")
    too_big = tmp_path / "huge.pkg"
    with too_big.open("wb") as stream:
        stream.truncate(1_000_000_001)
    with pytest.raises(EvidenceError, match="1\\.\\.1,000"):
        create_hardware_scaffold("roborock.vacuum.a75", "1.2.3",
                                 too_big, tmp_path / "huge.json")
    assert not (tmp_path / "huge.json").exists()


def test_draft_can_be_reviewed_but_not_authorize_install(tmp_path):
    p = tmp_path / "c.pkg"; p.write_bytes(b"pkg")
    report = tmp_path / "evidence.json"
    create_hardware_scaffold("roborock.vacuum.a75", "1.2.3", p, report)
    evidence = json.loads(report.read_text())
    for item in FIELDS:
        evidence["observations"][item] = {
            "observed": True,
            "reference": "https://example.org/public/evidence/" + item,
        }
    assessment = assess_hardware_acceptance(evidence)
    assert assessment["status"] == "ready-for-independent-hardware-review"
    assert assessment["evidence_independently_verified"] is False
    assert assessment["install_authorized"] is False


def test_cli_scaffold_and_existing_readonly_assessment(tmp_path):
    package = tmp_path / "candidate.pkg"
    package.write_bytes(b"candidate")
    path = tmp_path / "draft.json"
    base = [sys.executable, "-m", "vacuum_voice_hub", "research"]
    help_ = subprocess.run(base + ["hardware-scaffold", "--help"],
                           capture_output=True, text=True, check=True)
    assert "--firmware" in help_.stdout and "--package" in help_.stdout
    result = subprocess.run(base + [
        "hardware-scaffold", "--model", "roborock.vacuum.a75",
        "--firmware", "1.2.3", "--package", str(package), "--output", str(path)
    ], capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    assert data["all_observations_unverified"]
    read = subprocess.run(base + [
        "hardware-acceptance", str(path), "--model", "roborock.vacuum.a75"
    ], capture_output=True, text=True, check=True)
    assert json.loads(read.stdout)["status"] == "incomplete-research-only"
