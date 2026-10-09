"""v1.8 local attributed voice library read-only index and stale-source QA."""
import json
import subprocess
import sys
import wave

import pytest

from vacuum_voice_hub.creator import new_workspace, assign_audio
from vacuum_voice_hub.voice_library import create_library, audit_library, search_library, reconcile_library


def make_workspace(tmp, identity, language, license_name="UNLICENSED"):
    root = tmp / identity
    new_workspace(root, pack_id=identity, name=identity+" Voice",
                  author="Studio contributor", language=language,
                  license_name=license_name)
    source = tmp / (identity + ".wav")
    with wave.open(str(source), "wb") as stream:
        stream.setnchannels(1);stream.setsampwidth(2);stream.setframerate(16000)
        stream.writeframes(b"\x00\x12" * 16000)
    assign_audio(root, "clean.start", source)
    return root


def test_create_search_reconcile_and_privacy(tmp_path):
    a = make_workspace(tmp_path, "voice_a", "uk")
    b = make_workspace(tmp_path, "voice_b", "en", "CC-BY-4.0")
    dest = tmp_path / "library.json"
    report = create_library([b, a], dest)
    assert report["pack_count"] == 2
    assert report["languages"] == ["en", "uk"]
    assert not report["rights_independently_verified"]
    assert not report["install_authorized"]
    assert str(tmp_path) not in dest.read_text("utf-8")
    assert "audio/clean.start.wav" not in dest.read_text("utf-8")
    assert search_library(dest, language="en")["matching_packs"] == 1
    assert search_library(dest, license_name="CC-BY-4.0")["matching_packs"] == 1
    assert search_library(dest, query="VOICE_A")["matching_packs"] == 1
    assert reconcile_library(dest, [a, b])["matches"]
    with pytest.raises(FileExistsError):
        create_library([a], dest)


def test_audio_changed_after_index_requires_reconciliation(tmp_path):
    p = make_workspace(tmp_path, "voice_a", "ru")
    out = tmp_path / "index.json"
    create_library([p], out)
    sound = p / "audio" / "clean.start.wav"
    sound.write_bytes(sound.read_bytes() + b"\x00")
    result = reconcile_library(out, [p])
    assert not result["matches"]
    assert result["modified_packs"] == ["voice_a"]
    assert audit_library(out)["pack_count"] == 1


def test_reject_invalid_or_duplicate_pack_ids(tmp_path):
    p = make_workspace(tmp_path, "voice_a", "en")
    with pytest.raises(ValueError, match="duplicate"):
        create_library([p, p], tmp_path / "duplicate.json")
    with pytest.raises(ValueError, match="1..128"):
        create_library([], tmp_path / "empty.json")


def test_reject_source_symlink(tmp_path):
    p = make_workspace(tmp_path, "voice_a", "en")
    link = tmp_path / "link"
    link.symlink_to(p, target_is_directory=True)
    with pytest.raises(ValueError, match="regular directory"):
        create_library([link], tmp_path / "index.json")


def test_reject_modified_and_duplicate_key_index(tmp_path):
    p = make_workspace(tmp_path, "voice_a", "en")
    dest = tmp_path / "index.json"
    create_library([p], dest)
    doc = json.loads(dest.read_text())
    doc["packs"][0]["rights_independently_verified"] = True
    dest.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="checksum"):
        audit_library(dest)
    dest.write_text('{"schema":"vvh.local-voice-library.v1","schema":"oops"}')
    with pytest.raises(ValueError, match="duplicate"):
        audit_library(dest)


def test_cli_workflow(tmp_path):
    p = make_workspace(tmp_path, "voice_a", "uk")
    index = tmp_path / "index.json"
    base = [sys.executable, "-m", "vacuum_voice_hub", "library"]
    def run(*opts):
        return json.loads(subprocess.run(base+list(opts), capture_output=True,
                                         text=True, check=True).stdout)
    assert run("index", "--workspace", str(p), "--output", str(index))["pack_count"] == 1
    assert run("audit", str(index))["pack_count"] == 1
    assert run("search", str(index), "--language", "uk")["matching_packs"] == 1
    assert run("reconcile", str(index), "--workspace", str(p))["matches"]
