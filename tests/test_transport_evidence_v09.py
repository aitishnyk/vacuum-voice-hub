import copy
import json
import pytest
from vacuum_voice_hub.transport_evidence import (
    EvidenceError, inspect_file, validate_evidence,
)

GOOD = {
    "schema": "vvh.transport-evidence.v1",
    "model_id": "xiaomi.vacuum.d101",
    "source": "https://example.org/research/voice-format",
    "package": {"sha256": "a" * 64, "size_bytes": 12345, "format": "unknown"},
    "observations": ["package_inspected"],
}


def test_research_only_cannot_authorize_install():
    result = validate_evidence(GOOD, expected_model="xiaomi.vacuum.d101")
    assert result["status"] == "research-only"
    assert result["install_authorized"] is False
    assert result["registry_mutated"] is False


def test_reported_device_success_requires_manual_hardware_review():
    row = copy.deepcopy(GOOD)
    row["observations"] = ["package_inspected", "device_downloaded", "device_reported_success"]
    row["hardware"] = {"firmware": "1.2.3"}
    result = validate_evidence(row)
    assert result["status"] == "hardware-review-required"
    assert not result["install_authorized"]


@pytest.mark.parametrize("change", [
    {"model_id": "other/model"},
    {"source": "http://example.org/a"},
    {"source": "https://user:pass@example.org/a"},
    {"package": {"sha256": "bad", "size_bytes": 1, "format": "zip"}},
    {"package": {"sha256": "a" * 64, "size_bytes": True, "format": "zip"}},
    {"observations": ["device_downloaded", "device_downloaded"]},
    {"token": "hidden"},
    {"hardware": {"firmware": ""}},
])
def test_invalid_or_sensitive_reports_fail_closed(change):
    row = copy.deepcopy(GOOD)
    row.update(change)
    with pytest.raises(EvidenceError):
        validate_evidence(row)


def test_cross_model_evidence_rejected():
    with pytest.raises(EvidenceError, match="model_id mismatch"):
        validate_evidence(GOOD, expected_model="xiaomi.vacuum.c102gl")


def test_bounded_file_intake(tmp_path):
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(GOOD), encoding="utf-8")
    assert inspect_file(path)["status"] == "research-only"
    path.write_bytes(b" " * (64 * 1024 + 1))
    with pytest.raises(EvidenceError, match="exceeds"):
        inspect_file(path)
