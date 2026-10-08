"""Regression tests for secure local voice archive extraction on Python 3.10+."""
import io
import tarfile
import zipfile

import pytest

from vacuum_voice_hub.archive import extract


def test_zip_and_tar_regular_files_extract_safely(tmp_path):
    zip_path = tmp_path / "good.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("nested/hello.ogg", b"OggS sample")
    out = tmp_path / "zip-out"
    extract(zip_path, out)
    assert (out / "nested" / "hello.ogg").read_bytes() == b"OggS sample"

    tar_path = tmp_path / "good.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tf:
        info = tarfile.TarInfo("./audio/123.ogg")
        payload = b"OggS sample"
        info.size = len(payload)
        tf.addfile(info, io.BytesIO(payload))
    out2 = tmp_path / "tar-out"
    extract(tar_path, out2)
    assert (out2 / "audio" / "123.ogg").read_bytes() == b"OggS sample"


@pytest.mark.parametrize("name", [
    "../escape.ogg", "/tmp/absolute.ogg", "C:/windows/drive.ogg",
    "dir/../../escape.ogg", "nested\\windows.ogg", "nested//empty.ogg",
])
def test_unsafe_zip_entry_refused_before_extract(tmp_path, name):
    src = tmp_path / "bad.zip"
    with zipfile.ZipFile(src, "w") as zf:
        zf.writestr("safe.ogg", b"untouched")
        zf.writestr(name, b"malicious")
    target = tmp_path / "dest"
    with pytest.raises(ValueError):
        extract(src, target)
    assert not (target / "safe.ogg").exists()


def test_duplicate_case_collisions_refused(tmp_path):
    src = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(src, "w") as zf:
        zf.writestr("Audio/start.ogg", b"a")
        zf.writestr("audio/START.ogg", b"b")
    with pytest.raises(ValueError, match="duplicate"):
        extract(src, tmp_path / "dest")


def test_file_directory_collision_refused(tmp_path):
    src = tmp_path / "collision.zip"
    with zipfile.ZipFile(src, "w") as zf:
        zf.writestr("audio", b"file")
        zf.writestr("audio/start.ogg", b"file")
    with pytest.raises(ValueError, match="collision"):
        extract(src, tmp_path / "dest")


def test_tar_symlinks_are_blocked(tmp_path):
    src = tmp_path / "symlink.tar.gz"
    with tarfile.open(src, "w:gz") as tf:
        t = tarfile.TarInfo("voice.ogg")
        t.type = tarfile.SYMTYPE
        t.linkname = "../../secret"
        tf.addfile(t)
    with pytest.raises(ValueError, match="unsafe"):
        extract(src, tmp_path / "dest")


def test_zip_unix_symlink_is_blocked(tmp_path):
    src = tmp_path / "symlink.zip"
    with zipfile.ZipFile(src, "w") as zf:
        info = zipfile.ZipInfo("voice.ogg")
        info.create_system = 3
        info.external_attr = 0o120777 << 16
        zf.writestr(info, b"/etc/passwd")
    with pytest.raises(ValueError, match="unsafe"):
        extract(src, tmp_path / "dest")


def test_safe_parent_symlink_cannot_escape_target(tmp_path):
    src = tmp_path / "symlink-parent.zip"
    with zipfile.ZipFile(src, "w") as zf:
        zf.writestr("nested/voice.ogg", b"payload")
    outside = tmp_path / "outside"
    outside.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()
    (dest / "nested").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="destination"):
        extract(src, dest)
    assert not (outside / "voice.ogg").exists()


def test_invalid_or_missing_container_rejected(tmp_path):
    src = tmp_path / "bad.bin"
    src.write_bytes(b"not zip or tar")
    with pytest.raises(ValueError, match="unsupported"):
        extract(src, tmp_path / "dest")
