"""Regressions for isolated Creator uploads and safe assignment paths."""
from pathlib import Path

import pytest

from vacuum_voice_hub.creator import assign_audio, assign_audio_bytes, new_workspace


def _project(tmp_path):
    root = tmp_path / "voice"
    new_workspace(
        root, pack_id="upload-safety", name="Upload safety",
        author="Contributor", language="en",
    )
    return root


def test_upload_preserves_existing_old_staging_filename(tmp_path):
    root = _project(tmp_path)
    old = root / "audio" / "_upload.wav"
    old.write_bytes(b"legacy user file - must remain untouched")

    result = assign_audio_bytes(root, "clean.start", "new.wav", b"new audio bytes")
    assert result["path"] == "audio/clean.start.wav"
    assert (root / result["path"]).read_bytes() == b"new audio bytes"
    assert old.read_bytes() == b"legacy user file - must remain untouched"
    assert sorted(p.name for p in (root / "audio").iterdir()) == [
        "_upload.wav", "clean.start.wav",
    ]


def test_invalid_event_cleans_up_private_staging_file(tmp_path):
    root = _project(tmp_path)
    with pytest.raises(ValueError, match="unknown semantic"):
        assign_audio_bytes(root, "not.a.real.event", "new.wav", b"some audio")
    assert list((root / "audio").iterdir()) == []


def test_symlink_assignment_does_not_replace_external_audio(tmp_path):
    root = _project(tmp_path)
    outside = tmp_path / "outside.wav"
    outside.write_bytes(b"keep this file")
    target = root / "audio" / "clean.start.wav"
    try:
        target.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Creating filesystem symlinks is unavailable")

    source = tmp_path / "source.wav"
    source.write_bytes(b"new voice")
    with pytest.raises(ValueError, match="symlinked"):
        assign_audio(root, "clean.start", source)
    assert outside.read_bytes() == b"keep this file"
    assert target.is_symlink()


def test_symlink_audio_directory_is_rejected_before_upload(tmp_path):
    root = _project(tmp_path)
    external_dir = tmp_path / "external"
    external_dir.mkdir()
    (root / "audio").rmdir()
    try:
        (root / "audio").symlink_to(external_dir, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating filesystem symlinks is unavailable")

    with pytest.raises(ValueError, match="real directory"):
        assign_audio_bytes(root, "clean.start", "new.wav", b"new audio")
    assert list(external_dir.iterdir()) == []
