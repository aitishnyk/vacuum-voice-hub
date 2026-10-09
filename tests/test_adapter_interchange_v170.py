"""v1.7 deterministic local adapter interchange and hostile-input handling."""
import hashlib
import json
import subprocess
import sys
import wave
import zipfile

import pytest

from vacuum_voice_hub.adapter_interchange import (
    adapter_preflight, build_interchange, verify_interchange
)
from vacuum_voice_hub.creator import new_workspace, assign_audio


def fixture(tmp_path):
    root = tmp_path / "pack"
    new_workspace(root, pack_id="test_adapter",
                  name="Test", author="Test author", language="uk")
    clips = []
    for name in ("clean.start", "clean.pause"):
        clip = tmp_path / (name + ".wav")
        with wave.open(str(clip), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(16000)
            audio.writeframes(b"\x00\x28" * 16000)
        assign_audio(root, name, clip)
        clips.append(clip)
    descriptor = tmp_path / "adapter.json"
    descriptor.write_text(json.dumps({
        "schema": "vvh.adapter-descriptor.v1",
        "adapter_id": "sample-adapter", "model_id": "dreame.vacuum.r2209",
        "author": "Adapter maintainer", "license": "UNLICENSED",
        "entries": [
            {"semantic": "clean.start", "archive_name": "clean-start.wav"},
            {"semantic": "clean.pause", "archive_name": "clean-pause.wav"},
        ]
    }))
    return root, descriptor, clips


def test_build_verify_is_reproducible_and_never_vendor_signed(tmp_path):
    root, descriptor, clips = fixture(tmp_path)
    preview = adapter_preflight(root, descriptor)
    assert preview["ready_for_offline_interchange"] is True
    assert preview["install_authorized"] is False
    a, b = tmp_path / "a.zip", tmp_path / "b.zip"
    first = build_interchange(root, descriptor, a)
    second = build_interchange(root, descriptor, b)
    assert first["sha256"] == second["sha256"]
    assert first["clip_count"] == 2
    assert verify_interchange(a)["integrity_verified"] is True
    assert not verify_interchange(a)["install_authorized"]
    with zipfile.ZipFile(a) as archive:
        assert set(archive.namelist()) == {"audio/clean-start.wav",
                                           "audio/clean-pause.wav", "manifest.json"}
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["official_vendor_package"] is False
        assert manifest["model_id"] == "dreame.vacuum.r2209"
        assert str(tmp_path) not in json.dumps(manifest)
    assert hashlib.sha256(clips[0].read_bytes()).hexdigest() == hashlib.sha256(
        (tmp_path / "clean.start.wav").read_bytes()).hexdigest()
    with pytest.raises(FileExistsError):
        build_interchange(root, descriptor, a)


def test_bad_descriptors_fail_closed(tmp_path):
    root, descriptor, _ = fixture(tmp_path)
    baseline = json.loads(descriptor.read_text())
    for patch in [
        {"model_id": "x10"},
        {"entries": []},
        {"adapter_id": "../unsafe"},
        {"entries": [{"semantic": "unknown.semantic", "archive_name": "x.wav"}]},
        {"entries": [{"semantic": "clean.start", "archive_name": "../evil.wav"}]},
        {"entries": [{"semantic": "clean.start", "archive_name": "ok.mp3"}]},
        {"entries": [{"semantic": "clean.start", "archive_name": "same.wav"},
                     {"semantic": "clean.pause", "archive_name": "same.wav"}]},
    ]:
        descriptor.write_text(json.dumps({**baseline, **patch}))
        with pytest.raises((ValueError, KeyError)):
            adapter_preflight(root, descriptor)
    descriptor.write_text(json.dumps(baseline))


def test_symlinks_and_duplicate_json_refused(tmp_path):
    root, descriptor, clips = fixture(tmp_path)
    shortcut = tmp_path / "adapter-link.json"
    shortcut.symlink_to(descriptor)
    with pytest.raises(ValueError, match="regular"):
        adapter_preflight(root, shortcut)
    descriptor.write_text('{"schema":"vvh.adapter-descriptor.v1","schema":"x"}')
    with pytest.raises(ValueError, match="duplicate"):
        adapter_preflight(root, descriptor)


def test_corrupt_archive_detected_and_not_authorized(tmp_path):
    root, descriptor, _ = fixture(tmp_path)
    output = tmp_path / "valid.zip"
    build_interchange(root, descriptor, output)
    damaged = tmp_path / "damaged.zip"
    with zipfile.ZipFile(output) as old, zipfile.ZipFile(damaged, "w") as new:
        for item in old.infolist():
            data = old.read(item.filename)
            if item.filename == "audio/clean-start.wav":
                data = data[:-4] + b"X" * 4
            new.writestr(item, data)
    with pytest.raises(ValueError, match="checksum"):
        verify_interchange(damaged)


def test_forged_manifest_cannot_claim_other_model_events(tmp_path):
    root, descriptor, _ = fixture(tmp_path)
    valid = tmp_path / "valid.zip"
    forged = tmp_path / "forged.zip"
    build_interchange(root, descriptor, valid)
    with zipfile.ZipFile(valid) as old, zipfile.ZipFile(forged, "w") as modified:
        for member in old.infolist():
            content = old.read(member)
            if member.filename == "manifest.json":
                payload = json.loads(content)
                payload["entries"][0]["target_event_ids"] = [999999]
                content = json.dumps(payload).encode("utf-8")
            modified.writestr(member, content)
    with pytest.raises(ValueError, match="mapping"):
        verify_interchange(forged)


def test_cli_adapter_workflow(tmp_path):
    root, descriptor, _ = fixture(tmp_path)
    output = tmp_path / "from-cli.zip"
    cmd = [sys.executable, "-m", "vacuum_voice_hub", "adapter"]
    def run(*parts):
        return json.loads(subprocess.run(cmd + list(parts), text=True,
                                         capture_output=True, check=True).stdout)
    assert run("preflight", "--workspace", str(root),
               "--descriptor", str(descriptor))["ready_for_offline_interchange"]
    assert run("build", "--workspace", str(root),
               "--descriptor", str(descriptor), "--output", str(output))["clip_count"] == 2
    assert run("verify", str(output))["integrity_verified"] is True
