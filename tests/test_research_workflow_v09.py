"""End-to-end offline v0.9 candidate intake and fail-closed regressions."""
import hashlib
import json
import subprocess
import sys
import tarfile
import io
import zipfile

import pytest

from vacuum_voice_hub.catalog import event_profile_for_model
from vacuum_voice_hub.research_pipeline import ResearchError, assess_candidate


def _candidate(tmp_path, model="dreame.vacuum.r2209"):
    path = tmp_path / "candidate.zip"
    ids = event_profile_for_model(model)["known_event_ids"][:6]
    with zipfile.ZipFile(path, "w") as z:
        for ident in ids:
            z.writestr(f"audio/{ident}.ogg", b"OggS sample")
    return path


def _evidence(path, model_id="dreame.vacuum.r2209", format_name="zip"):
    content = path.read_bytes()
    return {
        "schema": "vvh.transport-evidence.v1",
        "model_id": model_id,
        "source": "https://example.org/research/robot-voice-archive",
        "package": {
            "sha256": hashlib.sha256(content).hexdigest(),
            "size_bytes": len(content),
            "format": format_name,
        },
        "observations": ["package_inspected"],
    }


def test_candidate_model_coverage_and_non_installability(tmp_path):
    archive = _candidate(tmp_path)
    report = assess_candidate(archive, "dreame.vacuum.r2209")
    assert report["schema"] == "vvh.research-assessment.v1"
    assert report["findings"]["candidate_layout"] == "dreame-numeric-ogg-candidate"
    assert report["findings"]["matched_profile_numeric_ids"] == 6
    assert report["findings"]["outside_profile_numeric_ids"] == []
    assert not report["install_authorized"]
    assert not report["hardware_verified_by_assessment"]
    assert not report["registry_mutated"]
    assert report["evidence_matched"] is False


def test_evidence_binds_exact_model_bytes_size_and_format(tmp_path):
    archive = _candidate(tmp_path)
    evidence = _evidence(archive)
    path = tmp_path / "proof.json"
    path.write_text(json.dumps(evidence), encoding="utf-8")
    report = assess_candidate(archive, "dreame.vacuum.r2209", evidence_path=path)
    assert report["evidence_matched"] is True
    assert report["evidence_assessment"]["package_format"] == "zip"
    assert report["install_authorized"] is False

    evidence["package"]["sha256"] = "0" * 64
    path.write_text(json.dumps(evidence), encoding="utf-8")
    with pytest.raises(ResearchError, match="SHA-256"):
        assess_candidate(archive, "dreame.vacuum.r2209", evidence_path=path)

    evidence = _evidence(archive)
    evidence["package"]["size_bytes"] += 1
    path.write_text(json.dumps(evidence), encoding="utf-8")
    with pytest.raises(ResearchError, match="size"):
        assess_candidate(archive, "dreame.vacuum.r2209", evidence_path=path)

    evidence = _evidence(archive, format_name="tar.gz")
    path.write_text(json.dumps(evidence), encoding="utf-8")
    with pytest.raises(ResearchError, match="format"):
        assess_candidate(archive, "dreame.vacuum.r2209", evidence_path=path)


def test_cross_device_evidence_rejected(tmp_path):
    archive = _candidate(tmp_path)
    evidence_path = tmp_path / "proof.json"
    evidence_path.write_text(json.dumps(_evidence(archive, "xiaomi.vacuum.d101")))
    with pytest.raises(ResearchError, match="model_id mismatch"):
        assess_candidate(archive, "dreame.vacuum.r2209", evidence_path=evidence_path)


def test_ijai_filename_heuristic_is_not_transport_proof(tmp_path):
    archive = tmp_path / "ijai.zip"
    with zipfile.ZipFile(archive, "w") as z:
        for i in range(6):
            z.writestr(f"sounds/sound_{i}.mp3", b"ID3" + bytes([i]))
    report = assess_candidate(archive, "ijai.vacuum.v2")
    assert report["findings"]["candidate_layout"] == "ijai-named-mp3-candidate"
    assert report["install_authorized"] is False


def test_opaque_pkg_allowed_only_as_metadata_not_validated_package(tmp_path):
    archive = tmp_path / "vendor.pkg"
    archive.write_bytes(b"vendor encrypted opaque bytes")
    report = assess_candidate(archive, "roborock.vacuum.s5")
    assert report["inspection"] == "opaque"
    assert report["inventory"] is None
    assert report["findings"]["candidate_layout"] == "opaque-proprietary-package"
    assert report["install_authorized"] is False


def test_malformed_zip_with_pkg_extension_is_not_opaque_fallback(tmp_path):
    archive = tmp_path / "malformed.pkg"
    archive.write_bytes(b"PK\x03\x04malformed not a zip")
    with pytest.raises(ResearchError):
        assess_candidate(archive, "roborock.vacuum.s5")


def test_traversal_archive_with_pkg_extension_rejected(tmp_path):
    archive = tmp_path / "unsafe.pkg"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("../unsafe.ogg", b"data")
    with pytest.raises(ResearchError, match="unsafe"):
        assess_candidate(archive, "roborock.vacuum.s5")


def test_tar_gzip_cross_checks_format(tmp_path):
    archive = tmp_path / "sample.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        info = tarfile.TarInfo("audio/123.ogg")
        content = b"OggSsample"
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))
    evidence_path = tmp_path / "proof.json"
    evidence_path.write_text(json.dumps(_evidence(archive, format_name="tar.gz")))
    report = assess_candidate(archive, "dreame.vacuum.r2209", evidence_path=evidence_path)
    assert report["inspection"] == "archive"
    assert report["evidence_matched"] is True


def test_cli_inspect_and_legacy_backlog(tmp_path):
    archive = _candidate(tmp_path)
    result = subprocess.run(
        [sys.executable, "-m", "vacuum_voice_hub", "research", "inspect",
         str(archive), "--model", "dreame.vacuum.r2209"],
        capture_output=True, text=True, check=True,
    )
    assert json.loads(result.stdout)["install_authorized"] is False
    backlog = subprocess.run(
        [sys.executable, "-m", "vacuum_voice_hub", "research"],
        capture_output=True, text=True, check=True,
    )
    assert backlog.returncode == 0


def test_cli_validate_evidence(tmp_path):
    archive = _candidate(tmp_path)
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(_evidence(archive)), encoding="utf-8")
    done = subprocess.run(
        [sys.executable, "-m", "vacuum_voice_hub", "research", "validate-evidence",
         str(path), "--model", "dreame.vacuum.r2209"],
        capture_output=True, text=True, check=True,
    )
    result = json.loads(done.stdout)
    assert result["status"] == "research-only"
    assert result["install_authorized"] is False
