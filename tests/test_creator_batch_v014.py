"""v0.14 offline multi-target preflight and batch creation invariants."""
import hashlib
import json
import math
import struct
import subprocess
import sys
import tarfile
import wave
import zipfile
from pathlib import Path

import pytest

from vacuum_voice_hub.creator import new_workspace, assign_audio
from vacuum_voice_hub.creator_batch import preflight_workspace, batch_build_workspace


SEMANTICS = ("clean.start", "clean.pause", "clean.complete",
             "error.main_brush", "locate.here")


def _audio(path, frequency=440):
    rate = 16000
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        samples = [int(3000 * math.sin(2 * math.pi * frequency * i / rate))
                   for i in range(rate // 3)]
        wav.writeframes(struct.pack("<" + "h" * len(samples), *samples))


@pytest.fixture
def workspace(tmp_path):
    root = tmp_path / "my-voice"
    new_workspace(root, pack_id="my-voice", name="My Voice",
                  author="Tester", language="ru", license_name="UNLICENSED")
    path = tmp_path / "audio.wav"
    for index, semantic in enumerate(SEMANTICS):
        _audio(path, 440 + 40 * index)
        assign_audio(root, semantic, path)
    return root


def test_preflight_does_not_mutate_source_and_reports_missing_core(workspace):
    before = sorted((p.name, p.stat().st_size) for p in workspace.rglob("*") if p.is_file())
    report = preflight_workspace(workspace, "dreame.vacuum.r2209", check_audio=True)
    after = sorted((p.name, p.stat().st_size) for p in workspace.rglob("*") if p.is_file())
    assert before == after
    assert report["schema"] == "vvh.creator-preflight.v1"
    assert report["ready"] is True
    assert report["model_id"] == "dreame.vacuum.r2209"
    assert report["mapped_event_count"] == 5
    assert len(report["mapped_event_ids"]) == 5
    assert report["missing_event_ids"]
    assert report["missing_core_event_ids"]
    assert report["core_event_count"] >= len(report["missing_core_event_ids"])
    assert report["audio_warnings"] == []
    assert all(len(x["sha256"]) == 64 for x in report["inputs"])
    assert report["install_authorized"] is False
    assert report["custom_install_verified_by_preflight"] is False


def test_insufficient_events_remains_not_ready(tmp_path):
    root = tmp_path / "small"
    new_workspace(root, pack_id="small", name="Small", author="QA", language="en")
    path = tmp_path / "test.wav"
    _audio(path)
    assign_audio(root, "clean.start", path)
    result = preflight_workspace(root, "dreame.vacuum.r2209")
    assert result["ready"] is False
    assert result["mapped_event_count"] == 1


def test_preflight_detects_conflicting_sources_without_overwriting(workspace, monkeypatch):
    import vacuum_voice_hub.creator_batch as batch
    from vacuum_voice_hub.catalog import event_by_semantic
    def conflicting(semantic):
        if semantic == "clean.pause":
            return event_by_semantic("clean.start")
        return event_by_semantic(semantic)
    monkeypatch.setattr(batch, "event_by_semantic", conflicting)
    result = batch.preflight_workspace(workspace, "dreame.vacuum.r2209")
    assert result["ready"] is False
    assert result["collisions"]
    assert result["collisions"][0]["semantics"] == ["clean.pause", "clean.start"]


def test_batch_two_models_creates_independent_packages_and_sha_manifest(workspace, tmp_path):
    dest = tmp_path / "batch-out"
    before = (workspace / "manifest.json").read_bytes()
    report = batch_build_workspace(
        workspace, ["dreame.vacuum.r2209", "viomi.vacuum.v60"], dest,
        check_audio=True,
    )
    assert report["schema"] == "vvh.creator-batch.v1"
    assert report["model_count"] == 2
    assert report["install_authorized"] is False
    assert report["license_review_required"] is True
    assert report["models"] == ["dreame.vacuum.r2209", "viomi.vacuum.v60"]
    assert len(report["packages"]) == 2
    assert (workspace / "manifest.json").read_bytes() == before
    recorded = json.loads((dest / "manifest.json").read_text())
    assert recorded["models"] == report["models"]
    for row in report["packages"]:
        path = dest / row["file"]
        assert path.is_file()
        assert row["bytes"] == path.stat().st_size
        assert row["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert not row["install_authorized"]
        assert not row["manufacturer_format_verified"]
    first = dest / report["packages"][0]["file"]
    second = dest / report["packages"][1]["file"]
    assert first.suffix == ".gz"
    assert second.suffix == ".zip"
    with tarfile.open(first, "r:gz") as archive:
        assert len(archive.getnames()) >= 5
    with zipfile.ZipFile(second) as archive:
        assert "manifest.json" in archive.namelist()
        assert len([x for x in archive.namelist() if x.startswith("audio/")]) >= 5


def test_batch_refuses_existing_directory_and_preserves_its_files(workspace, tmp_path):
    dest = tmp_path / "keep"
    dest.mkdir()
    prior = dest / "important.txt"
    prior.write_text("DO NOT CHANGE")
    with pytest.raises(FileExistsError):
        batch_build_workspace(workspace, ["viomi.vacuum.v60"], dest)
    assert prior.read_text() == "DO NOT CHANGE"


def test_batch_rejects_canonical_duplicate_and_inside_workspace(workspace, tmp_path):
    with pytest.raises(ValueError, match="duplicate"):
        batch_build_workspace(workspace,
                              ["dreame.vacuum.r2209", "dreame.vacuum.r2209"],
                              tmp_path / "duplicate")
    assert not (tmp_path / "duplicate").exists()
    with pytest.raises(ValueError, match="outside"):
        batch_build_workspace(workspace, ["dreame.vacuum.r2209"], workspace / "output")
    assert not (workspace / "output").exists()


def test_batch_requires_1_to_16_targets_and_exact_existing_models(workspace, tmp_path):
    for models in ([], ["viomi.vacuum.v60"] * 17, "viomi.vacuum.v60"):
        with pytest.raises(ValueError):
            batch_build_workspace(workspace, models, tmp_path / "out")
    with pytest.raises(KeyError):
        batch_build_workspace(workspace, ["nonexistent.robot"], tmp_path / "out")


def test_batch_failed_second_build_cleans_own_output_not_user_files(workspace, tmp_path, monkeypatch):
    import vacuum_voice_hub.creator_batch as batch
    build = batch.build_workspace
    counter = {"n": 0}
    def fail_second(*args, **kwargs):
        counter["n"] += 1
        if counter["n"] == 2:
            raise RuntimeError("intentional second-model failure")
        return build(*args, **kwargs)
    monkeypatch.setattr(batch, "build_workspace", fail_second)
    unrelated = tmp_path / "other.txt"
    unrelated.write_text("KEEP")
    dest = tmp_path / "new-batch"
    with pytest.raises(RuntimeError, match="intentional"):
        batch.batch_build_workspace(workspace,
                                   ["dreame.vacuum.r2209", "viomi.vacuum.v60"],
                                   dest)
    assert not dest.exists()
    assert unrelated.read_text() == "KEEP"
    assert (workspace / "manifest.json").is_file()


def test_batch_refuses_source_changed_during_conversion(workspace, tmp_path, monkeypatch):
    import vacuum_voice_hub.creator_batch as batch
    build = batch.build_workspace
    def edit_source(*args, **kwargs):
        result = build(*args, **kwargs)
        path = workspace / "audio" / "clean.start.wav"
        _audio(path, 1200)
        return result
    monkeypatch.setattr(batch, "build_workspace", edit_source)
    dest = tmp_path / "batch"
    with pytest.raises(RuntimeError, match="changed"):
        batch.batch_build_workspace(workspace, ["dreame.vacuum.r2209"], dest)
    assert not dest.exists()


def test_cli_preflight_and_batch_help_are_available(workspace):
    base = [sys.executable, "-m", "vacuum_voice_hub", "creator"]
    p = subprocess.run(base + ["preflight", str(workspace), "--model", "dreame.vacuum.r2209"],
                       check=True, text=True, capture_output=True)
    report = json.loads(p.stdout)
    assert report["ready"]
    assert report["install_authorized"] is False
    result = subprocess.run(base + ["batch", "--help"],
                            check=True, text=True, capture_output=True)
    assert "--output-dir" in result.stdout
    assert "--model" in result.stdout
