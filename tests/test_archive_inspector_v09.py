import io
import tarfile
import zipfile

import pytest
from vacuum_voice_hub.archive_inspector import (
    ArchiveInspectionError, inspect_archive, inspect_to_json
)


def test_zip_audio_inventory(tmp_path):
    p = tmp_path / "sounds.zip"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("audio/start.ogg", b"sound")
        z.writestr("notes.txt", b"metadata")
    out = inspect_archive(p)
    assert out["container"] == "zip"
    assert out["audio_count"] == 1
    assert out["file_count"] == 2
    assert out["install_authorized"] is False
    assert out["hardware_verified"] is False
    assert "vvh.archive-inventory.v1" in inspect_to_json(p)


def test_tar_audio_inventory(tmp_path):
    p = tmp_path / "sounds.tar.gz"
    with tarfile.open(p, "w:gz") as tar:
        payload = b"voice"
        info = tarfile.TarInfo("sounds/123.ogg")
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    out = inspect_archive(p)
    assert out["container"] == "tar"
    assert out["audio_count"] == 1


@pytest.mark.parametrize("names", [
    ["../escape.ogg"], ["/abs.wav"], ["C:/device.mp3"],
    ["a.ogg", "A.ogg"], ["a\\bad.ogg"], ["./voice.ogg"]
])
def test_zip_unsafe_names_fail_closed(tmp_path, names):
    p = tmp_path / "bad.zip"
    with zipfile.ZipFile(p, "w") as z:
        for name in names:
            z.writestr(name, b"data")
    with pytest.raises(ArchiveInspectionError):
        inspect_archive(p)


def test_tar_symlink_rejected(tmp_path):
    p = tmp_path / "link.tar.gz"
    with tarfile.open(p, "w:gz") as tar:
        item = tarfile.TarInfo("escape.ogg")
        item.type = tarfile.SYMTYPE
        item.linkname = "../../secret"
        tar.addfile(item)
    with pytest.raises(ArchiveInspectionError, match="special tar"):
        inspect_archive(p)


def test_oversized_member_rejected(tmp_path):
    p = tmp_path / "oversize.zip"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("x.ogg", b"x" * (16 * 1024 * 1024 + 1))
    with pytest.raises(ArchiveInspectionError, match="oversized"):
        inspect_archive(p)


def test_unknown_container_rejected(tmp_path):
    p = tmp_path / "unknown.bin"
    p.write_bytes(b"not-a-package")
    with pytest.raises(ArchiveInspectionError, match="unsupported"):
        inspect_archive(p)
