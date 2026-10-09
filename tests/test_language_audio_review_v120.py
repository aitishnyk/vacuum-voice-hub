"""v1.2 local native-speaker review and read-only audio A/B regression."""
import hashlib
import json
import math
import struct
import subprocess
import sys
import wave

import pytest

from vacuum_voice_hub.language_review import (
    create_language_review, audit_language_review, mark_language_review
)
from vacuum_voice_hub.audio_compare import compare_audio

MODEL = "dreame.vacuum.r2209"


def _overlay(path, text="Перевірте бампер робота."):
    p = path / "translation.json"
    p.write_text(json.dumps({
        "schema": "vvh.translation-overlay.v1", "locale": "uk",
        "author": "Contributor", "license": "UNLICENSED",
        "source_url": None, "translations": {"error.bumper": text},
    }, ensure_ascii=False), encoding="utf-8")
    return p


def _wav(path, amplitude):
    frames = [round(amplitude * math.sin(2 * math.pi * 440 * n / 16000))
              for n in range(16000)]
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(struct.pack("<" + "h" * len(frames), *frames))


def test_review_scaffold_is_pending_and_never_claims_hardware(tmp_path):
    raw = tmp_path / "initial.json"
    got = create_language_review("uk", MODEL, raw)
    assert got["entries"] >= 16
    initial = audit_language_review(raw)
    assert initial["counts"]["pending"] == got["entries"]
    assert initial["human_approval_claims"] == 0
    assert not initial["native_speaker_independently_verified"]
    assert not initial["install_authorized"]
    with pytest.raises(FileExistsError):
        create_language_review("uk", MODEL, raw)


def test_attributed_decision_is_copy_on_write_with_approval_gate(tmp_path):
    old, new = tmp_path / "old.json", tmp_path / "new.json"
    create_language_review("uk", MODEL, old)
    original = hashlib.sha256(old.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="attestation"):
        mark_language_review(old, "clean.start", "approved", new, reviewer="Volunteer")
    assert not new.exists()
    mark_language_review(old, "clean.start", "approved", new,
                         reviewer="Volunteer", language_attested=True)
    assert hashlib.sha256(old.read_bytes()).hexdigest() == original
    result = audit_language_review(new)
    assert result["counts"]["approved"] == 1
    assert result["counts"]["pending"] == result["entries"] - 1
    assert not result["rights_independently_verified"]
    with pytest.raises(FileExistsError):
        mark_language_review(old, "clean.start", "approved", new,
                             reviewer="Volunteer", language_attested=True)


def test_review_overlay_must_match_current_text(tmp_path):
    p = _overlay(tmp_path)
    draft = tmp_path / "draft.json"
    create_language_review("uk", MODEL, draft, overlay_path=p)
    assert audit_language_review(draft, overlay_path=p)["snapshot_current"]
    with pytest.raises(ValueError, match="required"):
        audit_language_review(draft)
    _overlay(tmp_path, "Інший переклад.")
    with pytest.raises(ValueError, match="stale"):
        audit_language_review(draft, overlay_path=p)


def test_review_rejects_tampered_phrases_claims_and_duplicate_keys(tmp_path):
    draft = tmp_path / "draft.json"
    create_language_review("uk", MODEL, draft)
    doc = json.loads(draft.read_text())
    doc["entries"][0]["text"] += "FAKE"
    draft.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="mapping"):
        audit_language_review(draft)
    draft.write_text('{"schema":"vvh.language-review.v1","schema":"vvh.language-review.v1"}')
    with pytest.raises(ValueError, match="duplicate"):
        audit_language_review(draft)


@pytest.mark.parametrize("status,reviewer,attest", [
    ("approved", None, True), ("approved", "Human", False),
    ("needs-changes", None, False), ("unknown", "Human", True),
])
def test_invalid_mark_refused(tmp_path, status, reviewer, attest):
    draft, output = tmp_path / "draft.json", tmp_path / "out.json"
    create_language_review("uk", MODEL, draft)
    with pytest.raises(ValueError):
        mark_language_review(draft, "clean.start", status, output,
                             reviewer=reviewer, language_attested=attest)
    assert not output.exists()


def test_audio_ab_read_only_with_usable_signal_deltas(tmp_path):
    first, second = tmp_path / "first.wav", tmp_path / "second.wav"
    _wav(first, 4000)
    _wav(second, 8000)
    before = (hashlib.sha256(first.read_bytes()).hexdigest(),
              hashlib.sha256(second.read_bytes()).hexdigest())
    report = compare_audio(first, second)
    assert report["a"]["sha256"] == before[0]
    assert report["b"]["sha256"] == before[1]
    assert 5 < report["b_minus_a"]["peak_dbfs"] < 7
    assert report["b_minus_a"]["duration_sec"] == 0
    assert report["source_audio_modified"] is False
    assert report["human_listening_required"] is True
    assert not report["install_authorized"]
    with pytest.raises(ValueError, match="different"):
        compare_audio(first, first)


def test_cli_review_and_ab(tmp_path):
    wav1, wav2 = tmp_path / "a.wav", tmp_path / "b.wav"
    _wav(wav1, 3000)
    _wav(wav2, 6000)
    root = [sys.executable, "-m", "vacuum_voice_hub"]
    def run(*args):
        proc = subprocess.run(root + list(args), capture_output=True, text=True, check=True)
        return json.loads(proc.stdout)
    initial, marked = tmp_path / "review.json", tmp_path / "marked.json"
    assert run("scripts", "review-init", "--language", "uk",
               "--model", MODEL, "--output", str(initial))["entries"] >= 16
    assert run("scripts", "review-mark", str(initial), "--semantic", "clean.start",
               "--status", "approved", "--reviewer", "Translator",
               "--language-attested", "--output", str(marked))["approved"]
    assert run("scripts", "review-audit", str(marked))["counts"]["approved"] == 1
    assert run("creator", "audio-compare", str(wav1), str(wav2))["schema"] == "vvh.audio-ab-review.v1"
