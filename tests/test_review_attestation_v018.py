"""Real Ed25519 review attestation and bounded audio acceptance regression."""
import base64
import hashlib
import json
import math
import struct
import subprocess
import sys
import wave

import pytest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from vacuum_voice_hub.creator import new_workspace, assign_audio
from vacuum_voice_hub.production_review import (
    create_review, mark_review, refresh_review)
from vacuum_voice_hub.reviewer_attestation import sign_review, verify_attestation
from vacuum_voice_hub.review_audio_acceptance import inspect_review_audio


def _tone(path, frequency=440):
    samples = [int(6000 * math.sin(2 * math.pi * frequency * i / 16000))
               for i in range(16000)]
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(16000)
        stream.writeframes(struct.pack("<" + "h" * len(samples), *samples))


@pytest.fixture
def reviewed(tmp_path):
    project = tmp_path / "workspace"
    new_workspace(project, pack_id="v018-test", name="Review", author="QA",
                  language="ru", license_name="UNLICENSED")
    audio = tmp_path / "original.wav"
    _tone(audio)
    assign_audio(project, "clean.start", audio)
    review = tmp_path / "review.json"
    create_review(project, "ru", "dreame.vacuum.r2209", review)
    mark_review(review, "clean.start", "recorded")
    mark_review(review, "clean.start", "listened", reviewer="Human")
    mark_review(review, "clean.start", "approved", reviewer="Human",
                language_attested=True, rights_attested=True)
    return project, review


@pytest.fixture
def keys(tmp_path):
    private = Ed25519PrivateKey.generate()
    secret = tmp_path / "owned-private.pem"
    public = tmp_path / "reviewer-public.pem"
    secret.write_bytes(private.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()))
    public.write_bytes(private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    return secret, public


def test_ed25519_attestation_round_trip_actual_crypto(reviewed, keys, tmp_path):
    project, review = reviewed
    secret, public = keys
    original = (project / "audio" / "clean.start.wav").read_bytes()
    output = tmp_path / "signed-attestation.json"
    signed = sign_review(review, "clean.start", secret, output)
    assert signed["signature_created"] is True
    assert signed["install_authorized"] is False
    checked = verify_attestation(output, public, review)
    assert checked["signature_valid"]
    assert checked["source_snapshot_matches"]
    assert not checked["signer_identity_independently_verified"]
    assert not checked["copyright_rights_independently_verified"]
    assert not checked["spoken_language_verified"]
    assert not checked["install_authorized"]
    assert (project / "audio" / "clean.start.wav").read_bytes() == original
    with pytest.raises(FileExistsError):
        sign_review(review, "clean.start", secret, output)


def test_attestation_rejects_tampered_signed_fields(reviewed, keys, tmp_path):
    _, review = reviewed
    private, public = keys
    dest = tmp_path / "original-attestation.json"
    sign_review(review, "clean.start", private, dest)
    doc = json.loads(dest.read_text())
    doc["payload"]["rights_attested"] = False
    dest.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="signature"):
        verify_attestation(dest, public, review)


def test_attestation_rejects_wrong_key(reviewed, keys, tmp_path):
    _, review = reviewed
    private, public = keys
    output = tmp_path / "sig.json"
    sign_review(review, "clean.start", private, output)
    wrong = Ed25519PrivateKey.generate()
    wrong_pub = tmp_path / "wrong.pem"
    wrong_pub.write_bytes(wrong.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    with pytest.raises(ValueError, match="fingerprint"):
        verify_attestation(output, wrong_pub, review)


def test_signature_fails_after_audio_mutation(reviewed, keys, tmp_path):
    project, review = reviewed
    secret, public = keys
    dest = tmp_path / "sig.json"
    sign_review(review, "clean.start", secret, dest)
    _tone(project / "audio" / "clean.start.wav", frequency=700)
    with pytest.raises(ValueError, match="stale|mismatch"):
        verify_attestation(dest, public, review)


def test_unapproved_review_cannot_be_signed(tmp_path, keys):
    root = tmp_path / "empty"
    new_workspace(root, pack_id="empty", name="Empty", author="QA", language="ru")
    review = tmp_path / "empty-review.json"
    create_review(root, "ru", "dreame.vacuum.r2209", review)
    with pytest.raises(ValueError, match="recording"):
        sign_review(review, "clean.start", keys[0], tmp_path / "no.json")


def test_human_and_signal_qa_are_distinct(reviewed):
    project, review = reviewed
    report = inspect_review_audio(review, max_clips=16)
    assert report["schema"] == "vvh.review-audio-acceptance.v1"
    assert report["total_recorded"] == 1
    assert report["human_approved"] == 1
    assert report["inspected"] == 1
    assert report["signal_passed"] == 1
    assert report["remaining_uninspected"] == 0
    assert report["clips"][0]["human_review_status"] == "approved"
    assert report["clips"][0]["signal_status"] == "inspected"
    assert not report["speaker_language_automatically_verified"]
    assert not report["rights_independently_verified"]
    assert not report["install_authorized"]


def test_audio_qa_limits_and_stale_protection(reviewed, tmp_path):
    project, review = reviewed
    for count in (0, -1, 33, "4", True):
        with pytest.raises(ValueError, match="max_clips"):
            inspect_review_audio(review, max_clips=count)
    _tone(project / "audio" / "clean.start.wav", frequency=900)
    with pytest.raises(ValueError, match="stale|mismatched"):
        inspect_review_audio(review)


def test_cli_help_attestation_and_audio_acceptance():
    base = [sys.executable, "-m", "vacuum_voice_hub", "creator", "review"]
    for action, flag in (("attest", "--private-key"),
                         ("verify-attestation", "--public-key"),
                         ("audio-acceptance", "--max-clips")):
        result = subprocess.run(base + [action, "--help"], check=True,
                                capture_output=True, text=True)
        assert flag in result.stdout
