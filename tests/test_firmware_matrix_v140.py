"""Firmware evidence matrix is read-only, model-specific, source-redacted."""
import hashlib
import json
import subprocess
import sys
import pytest

from vacuum_voice_hub.firmware_matrix import firmware_matrix
from vacuum_voice_hub.hardware_acceptance import FIELDS

MODEL = "dreame.vacuum.r2209"


def report(tmp, name, firmware="1.2.3", package="a", observed=(), model=MODEL):
    record = {
        "schema": "vvh.hardware-acceptance.v1",
        "model_id": model, "firmware": firmware,
        "package": {"sha256": package*64, "size_bytes": 1024},
        "observations": {key: {"observed": key in observed,
                               "reference": "https://example.org/report/" + key
                               if key in observed else None}
                         for key in FIELDS},
    }
    path = tmp / name
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


def test_only_metadata_no_auto_acceptance(tmp_path):
    path = report(tmp_path, "report.json")
    result = firmware_matrix(MODEL, [path])
    assert result["schema"] == "vvh.firmware-matrix.v1"
    assert result["report_count"] == 1
    assert result["reports"][0]["report_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert not result["per_firmware_hardware_verified"]
    assert not result["install_authorized"]
    assert result["firmwares"][0]["independent_acceptances"] == 0
    assert str(tmp_path) not in json.dumps(result)
    assert "https://example.org" not in json.dumps(result)


def test_all_observations_still_only_untrusted_claims(tmp_path):
    path = report(tmp_path, "complete.json", observed=FIELDS)
    result = firmware_matrix(MODEL, [path])
    assert result["firmwares"][0]["ready_for_independent_review"] == 1
    assert result["firmwares"][0]["independent_acceptances"] == 0
    assert not result["transport_policy_changed"]
    assert not result["install_authorized"]


def test_conflicts_and_multiple_firmwares(tmp_path):
    a = report(tmp_path, "a.json", package="a", observed=FIELDS)
    b = report(tmp_path, "b.json", package="b")
    c = report(tmp_path, "c.json", firmware="2.3.4")
    result = firmware_matrix(MODEL, [c, b, a])
    assert result["firmwares"][0]["needs_reconciliation"]
    assert result["firmwares"][0]["package_digest_count"] == 2
    assert len(result["firmwares"]) == 2


def test_duplicate_identical_claim_refused(tmp_path):
    a = report(tmp_path, "a.json")
    with pytest.raises(ValueError, match="duplicate"):
        firmware_matrix(MODEL, [a, a])


@pytest.mark.parametrize("mutation", [
    "wrong-model", "missing-step", "http-link", "bad-firmware", "sensitive-key",
])
def test_invalid_evidence_refused(tmp_path, mutation):
    p = report(tmp_path, "test.json")
    record = json.loads(p.read_text())
    if mutation == "wrong-model":
        record["model_id"] = "roborock.vacuum.a75"
    elif mutation == "missing-step":
        record["observations"].pop(FIELDS[0])
    elif mutation == "http-link":
        record["observations"][FIELDS[0]] = {"observed": True, "reference": "http://example.org"}
    elif mutation == "bad-firmware":
        record["firmware"] = "1.2.3\nPASSWORD"
    elif mutation == "sensitive-key":
        record["device_token"] = "secret"
    p.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        firmware_matrix(MODEL, [p])


def test_symlink_duplicate_json_and_size_fail_closed(tmp_path):
    p = report(tmp_path, "ok.json")
    link = tmp_path / "symlink.json"
    link.symlink_to(p)
    with pytest.raises(ValueError, match="regular"):
        firmware_matrix(MODEL, [link])
    p.write_text('{"schema":"vvh.hardware-acceptance.v1","schema":"oops"}')
    with pytest.raises(ValueError, match="duplicate"):
        firmware_matrix(MODEL, [p])
    p.write_bytes(b" "*65537)
    with pytest.raises(ValueError, match="65536"):
        firmware_matrix(MODEL, [p])


def test_report_count_bound(tmp_path):
    with pytest.raises(ValueError, match="1..64"):
        firmware_matrix(MODEL, [])
    with pytest.raises(ValueError, match="1..64"):
        firmware_matrix(MODEL, [tmp_path/"x"]*65)


def test_cli_firmware_matrix_without_robot_or_write(tmp_path):
    p = report(tmp_path, "report.json")
    cmd = [sys.executable, "-m", "vacuum_voice_hub", "research",
           "firmware-matrix", "--model", MODEL, "--report", str(p)]
    done = subprocess.run(cmd, capture_output=True, text=True, check=True)
    parsed = json.loads(done.stdout)
    assert parsed["report_count"] == 1
    assert parsed["registry_mutated"] is False
    assert parsed["install_authorized"] is False
