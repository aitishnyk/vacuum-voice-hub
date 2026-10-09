"""v1.9 non-destructive Creator backup, integrity and recovery acceptance."""
import hashlib
import json
import subprocess
import sys
import wave
import zipfile
import pytest

from vacuum_voice_hub.creator import new_workspace, assign_audio
from vacuum_voice_hub.creator_recovery import (
    create_backup, verify_backup, restore_backup, compare_backup
)


def workspace(tmp):
    root = tmp / "pack"
    new_workspace(root, pack_id="voice_backup", name="Backing up",
                  author="Creator", language="en", license_name="UNLICENSED")
    for semantic in ("clean.start", "clean.pause"):
        source = tmp / (semantic + ".wav")
        with wave.open(str(source), "wb") as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(16000)
            f.writeframes(b"\x00\x15" * 16000)
        assign_audio(root, semantic, source)
    return root


def test_backup_is_reproducible_and_restore_into_new_dir(tmp_path):
    root = workspace(tmp_path)
    a, b = tmp_path / "one.zip", tmp_path / "two.zip"
    result = create_backup(root, a)
    create_backup(root, b)
    assert result["audio_count"] == 2
    assert result["sha256"] == hashlib.sha256(b.read_bytes()).hexdigest()
    assert verify_backup(a)["integrity_verified"]
    assert compare_backup(a, root)["matches_backup"]
    dest = tmp_path / "restored"
    restored = restore_backup(a, dest)
    assert restored["recovery_verified"]
    assert restored["restored_clips"] == 2
    assert compare_backup(a, dest)["matches_backup"]
    with pytest.raises(FileExistsError):
        restore_backup(a, dest)
    with pytest.raises(FileExistsError):
        create_backup(root, a)


def test_changed_source_detected_without_automatic_restore(tmp_path):
    root = workspace(tmp_path)
    out = tmp_path / "backup.zip"
    create_backup(root, out)
    audio = root / "audio" / "clean.start.wav"
    audio.write_bytes(audio.read_bytes() + b"\x00")
    current = compare_backup(out, root)
    assert current["audio_changed"]
    assert not current["matches_backup"]
    assert not current["source_files_modified"]


def test_corrupt_zip_and_path_traversal_refused(tmp_path):
    root = workspace(tmp_path)
    src, damaged = tmp_path / "ok.zip", tmp_path / "bad.zip"
    create_backup(root, src)
    with zipfile.ZipFile(src) as reader, zipfile.ZipFile(damaged, "w") as target:
        for item in reader.infolist():
            data = reader.read(item)
            if item.filename.startswith("audio/"):
                data = data[:-1] + b"X"
            target.writestr(item, data)
    with pytest.raises(ValueError, match="checksum"):
        verify_backup(damaged)
    evil = tmp_path / "evil.zip"
    with zipfile.ZipFile(src) as original, zipfile.ZipFile(evil,"w") as dest:
        for item in original.infolist():
            dest.writestr("../escape" if item.filename.startswith("audio/") else item.filename,
                          original.read(item))
    with pytest.raises(ValueError, match="(duplicate|assignment|archive|unsafe)"):
        verify_backup(evil)
    assert not (tmp_path / "escape").exists()


def test_symlinked_recordings_refused(tmp_path):
    root = workspace(tmp_path)
    p = root / "audio" / "clean.start.wav"
    contents = p.read_bytes()
    p.unlink()
    outside = tmp_path / "elsewhere.wav"
    outside.write_bytes(contents)
    p.symlink_to(outside)
    with pytest.raises(ValueError):
        create_backup(root, tmp_path / "refused.zip")
    assert not (tmp_path / "refused.zip").exists()


def test_cli_round_trip(tmp_path):
    root = workspace(tmp_path)
    archive, restored = tmp_path / "cli.zip", tmp_path / "restored"
    base = [sys.executable, "-m", "vacuum_voice_hub", "creator"]
    def invoke(*args):
        return json.loads(subprocess.run(base+list(args), capture_output=True,
                                         text=True, check=True).stdout)
    assert invoke("backup", str(root), "--output", str(archive))["audio_count"] == 2
    assert invoke("backup-verify", str(archive))["integrity_verified"]
    assert invoke("backup-restore", str(archive), "--output-dir", str(restored))["recovery_verified"]
    assert invoke("backup-compare", str(archive), "--workspace", str(restored))["matches_backup"]
