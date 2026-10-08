"""Schema and archive path-boundary checks for the v0.9 research contract."""
import json
import tarfile
import zipfile
from pathlib import Path

import pytest

from vacuum_voice_hub.archive_inspector import ArchiveInspectionError, inspect_archive
from vacuum_voice_hub.research_pipeline import ResearchError, assess_candidate
from vacuum_voice_hub.transport_evidence import validate_evidence

ROOT = Path(__file__).resolve().parents[1]


def test_all_new_contract_files_are_valid_json():
    for name in ("transport-evidence", "archive-inventory", "research-assessment"):
        doc = json.loads((ROOT / "schemas" / f"vvh.{name}.v1.schema.json").read_text())
        assert doc["$schema"].endswith("/2020-12/schema")
        assert doc["properties"]["schema"]["const"] == f"vvh.{name}.v1"
    for name in ("archive-inventory", "research-assessment"):
        doc = json.loads((ROOT / "schemas" / f"vvh.{name}.v1.schema.json").read_text())
        assert doc["properties"]["install_authorized"]["const"] is False


def test_evidence_validator_exposes_only_validated_package_metadata():
    row = {
        "schema": "vvh.transport-evidence.v1",
        "model_id": "xiaomi.vacuum.d101",
        "source": "https://example.org/test",
        "package": {"sha256": "a" * 64, "size_bytes": 99, "format": "zip"},
        "observations": ["package_inspected"],
    }
    out = validate_evidence(row)
    assert out["package_size_bytes"] == 99
    assert out["package_format"] == "zip"
    assert not out["install_authorized"]


@pytest.mark.parametrize("name", ["../escape/", "./unsafe/", "/absolute/"])
def test_zip_directory_entry_cannot_hide_traversal(tmp_path, name):
    path = tmp_path / "malicious.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(name, b"")
        zf.writestr("sound.ogg", b"audio")
    with pytest.raises(ArchiveInspectionError):
        inspect_archive(path)


def test_tar_directory_entry_cannot_hide_traversal(tmp_path):
    path = tmp_path / "malicious.tar.gz"
    with tarfile.open(path, "w:gz") as tar:
        row = tarfile.TarInfo("../bad/")
        row.type = tarfile.DIRTYPE
        tar.addfile(row)
    with pytest.raises(ArchiveInspectionError):
        inspect_archive(path)


def test_disguised_unsafe_pkg_remains_rejected(tmp_path):
    path = tmp_path / "fake.pkg"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("../bad.ogg", b"unsafe")
    with pytest.raises(ResearchError):
        assess_candidate(path, "roborock.vacuum.s5")
