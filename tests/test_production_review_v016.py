"""v0.16 human-review production checklist, source-drift and unsafe export gates."""
import hashlib
import json
import math
import struct
import subprocess
import sys
import wave
import zipfile
from pathlib import Path

import pytest

from vacuum_voice_hub.catalog import models, voices
from vacuum_voice_hub.creator import assign_audio, new_workspace, remove_event
from vacuum_voice_hub.production_review import (
    audit_review, create_review, mark_review, refresh_review, export_review_bundle,
)


def _make_wav(path, freq=440):
    frames = [int(3000 * math.sin(2 * math.pi * freq * i / 16000))
              for i in range(16000)]
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(struct.pack("<" + "h" * len(frames), *frames))


@pytest.fixture
def project(tmp_path):
    path = tmp_path / "creator"
    new_workspace(path, pack_id="test-voice", name="Testing", author="Creator",
                  language="ru", license_name="UNLICENSED")
    audio = tmp_path / "input.wav"
    _make_wav(audio)
    assign_audio(path, "clean.start", audio)
    return path, audio


@pytest.fixture
def review(tmp_path, project):
    path = tmp_path / "review.json"
    result = create_review(project[0], "ru", "dreame.vacuum.r2209", path)
    assert result["schema"] == "vvh.production-review.v1"
    assert path.is_file()
    return path


def test_tasks_cover_model_event_profile_not_just_16_templates(review):
    record = json.loads(review.read_text())
    assert len(record["tasks"]) > 16
    assert all(r["event_ids"] for r in record["tasks"])
    assert len({r["semantic"] for r in record["tasks"]}) == len(record["tasks"])
    assert any(r["text"] is None for r in record["tasks"])
    assert any(r["text"] and r["audio"] for r in record["tasks"])
    assert record["install_authorized"] is False
    assert not record["license_automatically_verified"]
    assert not record["speaker_language_automatically_verified"]
    report = audit_review(review)
    assert report["valid"]
    assert report["status_counts"]["draft"] == report["total_tasks"]
    assert report["audio_present"] == 1
    assert not report["independent_language_verified"]


def test_status_requires_sequential_human_review_and_both_attestations(review):
    with pytest.raises(ValueError, match="invalid review transition"):
        mark_review(review, "clean.start", "approved", reviewer="Human")
    assert mark_review(review, "clean.start", "recorded")["status"] == "recorded"
    with pytest.raises(ValueError, match="human reviewer"):
        mark_review(review, "clean.start", "listened")
    assert mark_review(review, "clean.start", "listened", reviewer="Linguist")["status"] == "listened"
    with pytest.raises(ValueError, match="attestations"):
        mark_review(review, "clean.start", "approved", reviewer="Linguist")
    mark_review(review, "clean.start", "approved", reviewer="Linguist",
                note="I reviewed the supplied sample and attest rights.",
                language_attested=True, rights_attested=True)
    result = audit_review(review)
    assert result["status_counts"]["approved"] == 1
    assert result["approved_with_matching_audio"] == 1
    assert result["independent_rights_verified"] is False
    assert result["install_authorized"] is False


def test_cannot_approve_missing_audio(review):
    with pytest.raises(ValueError, match="recording required"):
        mark_review(review, "clean.pause", "recorded")
    assert audit_review(review)["valid"]


def test_review_stale_after_audio_or_manifest_change_is_not_approved(review, project):
    mark_review(review, "clean.start", "recorded")
    mark_review(review, "clean.start", "listened", reviewer="Listener")
    mark_review(review, "clean.start", "approved", reviewer="Listener",
                language_attested=True, rights_attested=True)
    source = project[0] / "audio" / "clean.start.wav"
    _make_wav(source, freq=700)
    changed = audit_review(review)
    assert not changed["valid"]
    assert any(row["issue"] == "audio-snapshot-mismatch" for row in changed["issues"])
    assert changed["approved_with_matching_audio"] == 0
    with pytest.raises(ValueError, match="stale"):
        mark_review(review, "clean.start", "draft")


def test_refresh_resets_changed_audio_but_preserves_unchanged_approval(tmp_path, project, review):
    mark_review(review, "clean.start", "recorded")
    mark_review(review, "clean.start", "listened", reviewer="Reader")
    mark_review(review, "clean.start", "approved", reviewer="Reader",
                language_attested=True, rights_attested=True)
    added = tmp_path / "second.wav"
    _make_wav(added, freq=510)
    assign_audio(project[0], "clean.pause", added)
    assert not audit_review(review)["valid"]
    refreshed = refresh_review(review)
    assert refreshed["audit"]["valid"]
    assert refreshed["audit"]["approved_with_matching_audio"] == 1
    assert refreshed["audit"]["audio_present"] == 2
    assert refreshed["retained"] >= 1
    _make_wav(project[0] / "audio" / "clean.start.wav", freq=620)
    refreshed = refresh_review(review)
    assert refreshed["audit"]["approved_with_matching_audio"] == 0
    assert next(x for x in json.loads(review.read_text())["tasks"]
                if x["semantic"] == "clean.start")["review"]["status"] == "draft"


def test_mutation_of_translated_task_text_is_detected(review):
    item = json.loads(review.read_text())
    task = next(row for row in item["tasks"] if row["semantic"] == "clean.start")
    task["text"] = "falsified"
    review.write_text(json.dumps(item))
    with pytest.raises(ValueError, match="identity/text altered"):
        audit_review(review)


def test_duplicate_json_keys_and_oversized_review_fails(review):
    review.write_text('{"schema":"vvh.production-review.v1","schema":"wrong"}')
    with pytest.raises(ValueError, match="duplicate"):
        audit_review(review)
    review.write_bytes(b" " * (512 * 1024 + 1))
    with pytest.raises(ValueError, match="larger"):
        audit_review(review)


def test_bundle_default_has_no_audio_and_no_private_machine_path(review, tmp_path):
    output = tmp_path / "review-only.zip"
    result = export_review_bundle(review, output)
    assert result["audio_included"] is False
    with zipfile.ZipFile(output) as bundle:
        assert sorted(bundle.namelist()) == ["audit.json", "review.json"]
        data = json.loads(bundle.read("review.json"))
        assert "workspace" not in data
        assert data["human_review_not_independent_verification"] is True
        assert data["install_authorized"] is False
    assert result["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    with pytest.raises(FileExistsError):
        export_review_bundle(review, output)


def test_audio_inclusion_is_explicit_and_content_hash_matches(review, tmp_path, project):
    output = tmp_path / "review-with-audio.zip"
    result = export_review_bundle(review, output, include_audio=True)
    assert result["audio_included"] is True
    with zipfile.ZipFile(output) as bundle:
        names = bundle.namelist()
        assert len([p for p in names if p.startswith("audio/")]) == 1
        data = bundle.read("audio/audio/clean.start.wav")
        assert hashlib.sha256(data).hexdigest() == hashlib.sha256(
            (project[0] / "audio" / "clean.start.wav").read_bytes()).hexdigest()


def test_bundle_rejects_stale_review_and_does_not_create_output(review, project, tmp_path):
    _make_wav(project[0] / "audio" / "clean.start.wav", freq=720)
    dest = tmp_path / "no.zip"
    with pytest.raises(ValueError, match="stale"):
        export_review_bundle(review, dest)
    assert not dest.exists()


def test_snapshot_fails_if_review_output_is_inside_workspace(project):
    with pytest.raises(ValueError, match="outside"):
        create_review(project[0], "ru", "dreame.vacuum.r2209",
                      project[0] / "review.json")
    assert not (project[0] / "review.json").exists()


def test_cli_review_subcommands_do_not_connect_to_robots(project, tmp_path):
    base = [sys.executable, "-m", "vacuum_voice_hub", "creator", "review"]
    dest = tmp_path / "cli-review.json"
    out = subprocess.run(base + ["init", str(project[0]), "--language", "ru",
                                 "--model", "dreame.vacuum.r2209", "--output", str(dest)],
                         capture_output=True, text=True, check=True)
    assert json.loads(out.stdout)["total_tasks"] > 16
    out = subprocess.run(base + ["audit", str(dest)], capture_output=True, text=True, check=True)
    assert json.loads(out.stdout)["valid"]
    out = subprocess.run(base + ["bundle", str(dest), "--output", str(tmp_path/"bundle.zip")],
                         capture_output=True, text=True, check=True)
    assert json.loads(out.stdout)["audio_included"] is False


def test_catalog_preservation_and_audio_provenance():
    from vacuum_voice_hub.script_packs import list_locales
    assert len(models()) == 215
    assert len(voices()) == 55
    assert len(list_locales()) == 18
    assert [m["id"] for m in models() if m["device_tested"]] == ["dreame.vacuum.r2209"]


def test_zip_exclusive_creation_race_never_deletes_unrelated_file(review, tmp_path, monkeypatch):
    dest = tmp_path / "concurrent.zip"
    real_open = Path.open
    def create_concurrently(path, mode="r", *args, **kwargs):
        if path == dest and mode == "xb":
            dest.write_text("KEEP THIS EXISTING FILE")
            raise FileExistsError("created by other process")
        return real_open(path, mode, *args, **kwargs)
    monkeypatch.setattr(Path, "open", create_concurrently)
    with pytest.raises(FileExistsError):
        export_review_bundle(review, dest)
    assert dest.read_text() == "KEEP THIS EXISTING FILE"


def test_zip_size_limit_cleans_only_own_output(review, tmp_path, monkeypatch):
    import vacuum_voice_hub.production_review as prod
    monkeypatch.setattr(prod, "MAX_BUNDLE_BYTES", 64)
    dest = tmp_path / "too-big.zip"
    unrelated = tmp_path / "unrelated.txt"
    unrelated.write_text("KEEP")
    with pytest.raises(ValueError, match="100 MiB"):
        export_review_bundle(review, dest, include_audio=True)
    assert not dest.exists()
    assert unrelated.read_text() == "KEEP"
