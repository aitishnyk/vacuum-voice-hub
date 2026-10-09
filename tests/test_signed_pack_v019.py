"""v0.19 signed entire audio pack and metadata-only hardware evidence bundle."""
import hashlib
import json
import math
import struct
import subprocess
import sys
import wave
import zipfile

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from vacuum_voice_hub.creator import new_workspace, assign_audio
from vacuum_voice_hub.production_review import create_review, mark_review
from vacuum_voice_hub.signed_pack import sign_pack, verify_pack
from vacuum_voice_hub.firmware_evidence_bundle import (
    create_evidence_bundle, verify_evidence_bundle,
)


def _tone(path, hz=440):
    samples = [int(5000 * math.sin(2 * math.pi * hz * i / 16000))
               for i in range(16000)]
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(16000)
        out.writeframes(struct.pack("<" + "h" * len(samples), *samples))


@pytest.fixture
def workspace(tmp_path):
    root = tmp_path / "creator"
    new_workspace(root, pack_id="pack019", name="Pack", author="QA",
                  language="uk", license_name="UNLICENSED")
    for name, hz in [("clean.start", 440), ("clean.pause", 660)]:
        source = tmp_path / (name.replace(".", "_") + ".wav")
        _tone(source, hz)
        assign_audio(root, name, source)
    review = tmp_path / "review.json"
    create_review(root, "uk", "dreame.vacuum.r2209", review)
    for name in ("clean.start", "clean.pause"):
        mark_review(review, name, "recorded")
        mark_review(review, name, "listened", reviewer="reviewer")
        mark_review(review, name, "approved", reviewer="reviewer",
                    rights_attested=True, language_attested=True)
    return root, review


@pytest.fixture
def keys(tmp_path):
    key = Ed25519PrivateKey.generate()
    private = tmp_path / "private.pem"
    public = tmp_path / "public.pem"
    private.write_bytes(key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()))
    public.write_bytes(key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    return private, public


def test_sign_every_recording_and_verify_current_exact_source(workspace, keys, tmp_path):
    root, review = workspace
    private, public = keys
    signed = tmp_path / "signed-pack.json"
    result = sign_pack(review, private, signed, require_approved=True)
    assert result["audio_count"] == 2
    assert result["approved_count"] == 2
    assert result["all_recordings_human_approved"] is True
    record = json.loads(signed.read_text())
    assert record["private_key_included"] is False
    assert len(record["payload"]["recordings"]) == 2
    assert "signed_at" in record["payload"]
    assert not record["install_authorized"]
    verified = verify_pack(signed, public, review)
    assert verified["signature_valid"]
    assert verified["current_source_matches"]
    assert not verified["voice_rights_independently_verified"]
    assert not verified["manufacturer_install_authorized"]
    assert not verified["install_authorized"]
    with pytest.raises(FileExistsError):
        sign_pack(review, private, signed)


def test_signature_breaks_on_audio_mutation(workspace, keys, tmp_path):
    root, review = workspace
    signed = tmp_path / "signed.json"
    sign_pack(review, keys[0], signed)
    _tone(root / "audio" / "clean.pause.wav", 880)
    with pytest.raises(ValueError, match="stale|invalid|mismatch"):
        verify_pack(signed, keys[1], review)


def test_signed_payload_tamper_and_wrong_key_rejected(workspace, keys, tmp_path):
    _, review = workspace
    signed = tmp_path / "signed.json"
    sign_pack(review, keys[0], signed)
    data = json.loads(signed.read_text())
    data["payload"]["recordings"][0]["human_review_status"] = "draft"
    signed.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="signature"):
        verify_pack(signed, keys[1], review)
    other_key = Ed25519PrivateKey.generate()
    wrong = tmp_path / "wrong.pem"
    wrong.write_bytes(other_key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    with pytest.raises(ValueError, match="fingerprint"):
        verify_pack(signed, wrong, review)


def test_sign_pack_optional_reviewer_gate_and_no_audio(workspace, keys, tmp_path):
    root, review = workspace
    mark_review(review, "clean.pause", "draft")
    with pytest.raises(ValueError, match="approval"):
        sign_pack(review, keys[0], tmp_path / "not-approved.json", require_approved=True)
    result = sign_pack(review, keys[0], tmp_path / "partial.json")
    assert result["approved_count"] == 1
    assert not result["all_recordings_human_approved"]


def test_signed_duplicate_json_member_rejected(workspace, keys, tmp_path):
    _, review = workspace
    signed = tmp_path / "signed.json"
    sign_pack(review, keys[0], signed)
    data = signed.read_text()
    signed.write_text(data.replace('"algorithm": "Ed25519"', '"algorithm": "Ed25519", "algorithm": "Ed25519"'))
    with pytest.raises(ValueError, match="duplicate"):
        verify_pack(signed, keys[1], review)


def _evidence(path, package):
    content = package.read_bytes()
    record = {
        "schema": "vvh.hardware-acceptance.v1",
        "model_id": "roborock.vacuum.a75", "firmware": "v1.4-claim",
        "package": {"sha256": hashlib.sha256(content).hexdigest(),
                    "size_bytes": len(content)},
        "observations": {
            key: {"observed": False, "reference": None}
            for key in (
                "package_signature_reviewed", "device_download_observed",
                "device_playback_heard", "reboot_persistence_checked",
                "stock_rollback_tested")
        },
    }
    path.write_text(json.dumps(record))
    return record


def test_evidence_bundle_excludes_binary_and_verifies_candidate(tmp_path):
    package = tmp_path / "candidate.pkg"
    package.write_bytes(b"not executable, just a candidate fixture")
    report = tmp_path / "evidence.json"
    _evidence(report, package)
    original = package.read_bytes()
    output = tmp_path / "evidence.zip"
    made = create_evidence_bundle(report, package, output)
    assert made["candidate_package_included"] is False
    with zipfile.ZipFile(output) as z:
        assert sorted(z.namelist()) == ["assessment.json", "evidence.json", "manifest.json"]
        assert all(".pkg" not in entry for entry in z.namelist())
    verified = verify_evidence_bundle(output, package, expected_model="roborock.vacuum.a75")
    assert verified["valid"]
    assert verified["hardware_report_status"] == "incomplete-research-only"
    assert not verified["independently_verified"]
    assert not verified["install_authorized"]
    assert package.read_bytes() == original
    with pytest.raises(FileExistsError):
        create_evidence_bundle(report, package, output)
    assert package.read_bytes() == original


def test_evidence_detects_modified_candidate_and_wrong_model(tmp_path):
    package = tmp_path / "candidate.pkg"
    package.write_bytes(b"valid local candidate")
    report = tmp_path / "evidence.json"
    _evidence(report, package)
    bundle = tmp_path / "ok.zip"
    create_evidence_bundle(report, package, bundle)
    with pytest.raises(Exception, match="model"):
        verify_evidence_bundle(bundle, package, expected_model="viomi.vacuum.v60")
    package.write_bytes(b"changed candidate")
    with pytest.raises(ValueError, match="changed"):
        verify_evidence_bundle(bundle, package)


def test_evidence_rejects_manifest_tamper_and_unexpected_zip_members(tmp_path):
    package = tmp_path / "candidate.pkg"
    package.write_bytes(b"candidate")
    report = tmp_path / "evidence.json"
    _evidence(report, package)
    good = tmp_path / "original.zip"
    create_evidence_bundle(report, package, good)
    with zipfile.ZipFile(good) as z:
        members = {n: z.read(n) for n in z.namelist()}
    changed = tmp_path / "forged.zip"
    manifest = json.loads(members["manifest.json"])
    manifest["install_authorized"] = True
    members["manifest.json"] = json.dumps(manifest).encode()
    with zipfile.ZipFile(changed, "w") as z:
        for name, value in members.items():
            z.writestr(name, value)
    with pytest.raises(ValueError, match="manifest"):
        verify_evidence_bundle(changed, package)
    injection = tmp_path / "extra.zip"
    with zipfile.ZipFile(injection, "w") as z:
        for name, value in members.items():
            z.writestr(name, value)
        z.writestr("../evil.txt", b"NEVER EXTRACT")
    with pytest.raises(ValueError, match="unexpected"):
        verify_evidence_bundle(injection, package)
    assert not (tmp_path / "evil.txt").exists()


def test_cli_v019_subcommands_exist():
    for args, marker in [
        (["creator", "review", "sign-pack", "--help"], "--require-approved"),
        (["creator", "review", "verify-pack", "--help"], "--public-key"),
        (["research", "evidence-bundle", "--help"], "--package"),
        (["research", "verify-evidence-bundle", "--help"], "--model"),
    ]:
        result = subprocess.run([sys.executable, "-m", "vacuum_voice_hub", *args],
                                capture_output=True, text=True, check=True)
        assert marker in result.stdout
