"""v1.3 opt-in local pronunciation with real Piper input and negative tests."""
import json
import subprocess
import sys
import wave

import pytest

from vacuum_voice_hub.pronunciation import load_lexicon, pronounce, pronunciation_preview
from vacuum_voice_hub.script_packs import script_for_model

MODEL = "dreame.vacuum.r2209"


def glossary(tmp, rows=None, **options):
    obj = {"schema": "vvh.pronunciation-lexicon.v1", "locale": "uk",
           "author": "Volunteer", "license": "UNLICENSED",
           "entries": rows if rows is not None else
           [{"written": "прибирання", "spoken": "прибирАння"}]}
    obj.update(options)
    path = tmp / "glossary.json"
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    return path


def test_one_pass_lexicon_does_not_mutate_source_script(tmp_path):
    path = glossary(tmp_path, [
        {"written": "прибирання", "spoken": "приби-рання"},
        {"written": "приби-рання", "spoken": "BAD-CASCADE"}])
    before = script_for_model("uk", MODEL)
    doc = load_lexicon(path, "uk")
    assert pronounce("Три прибирання.", doc) == "Три приби-рання."
    assert "BAD-CASCADE" not in pronounce("Три прибирання.", doc)
    result = pronunciation_preview("uk", MODEL, path)
    assert result["modified"] >= 1
    assert result["base_translations_changed"] is False
    assert result["audio_files_generated"] is False
    assert result["install_authorized"] is False
    assert script_for_model("uk", MODEL) == before


@pytest.mark.parametrize("patch,reason", [
    ({"locale": "de"}, "locale"), ({"author": ""}, "author"),
    ({"license": ""}, "license"),
    ({"source_url": "http://evil.example"}, "HTTPS"),
    ({"entries": []}, "1..128"),
    ({"entries": [{"written": "x", "spoken": "x"}]}, "invalid"),
    ({"entries": [{"written": "Hi", "spoken": "bonjour"},
                  {"written": "hi", "spoken": "hola"}]}, "duplicate"),
    ({"entries": [{"written": "foo", "spoken": "a\nb"}]}, "invalid"),
])
def test_invalid_lexicons_fail_closed(tmp_path, patch, reason):
    with pytest.raises(ValueError, match=reason):
        load_lexicon(glossary(tmp_path, **patch), "uk")


def test_reject_duplicate_json_keys_and_symlink(tmp_path):
    path = glossary(tmp_path)
    link = tmp_path / "link.json"
    link.symlink_to(path)
    with pytest.raises(ValueError, match="regular"):
        load_lexicon(link, "uk")
    path.write_text('{"schema":"vvh.pronunciation-lexicon.v1",'
                    '"schema":"vvh.pronunciation-lexicon.v1"}')
    with pytest.raises(ValueError, match="duplicate"):
        load_lexicon(path, "uk")


def test_cli_provides_preview_and_optional_engine_flags(tmp_path):
    p = glossary(tmp_path)
    base = [sys.executable, "-m", "vacuum_voice_hub", "scripts"]
    out = subprocess.run(base + ["pronounce", "--language", "uk", "--lexicon", str(p)],
                         capture_output=True, text=True, check=True)
    assert json.loads(out.stdout)["lexicon_sha256"] == load_lexicon(p, "uk")["sha256"]
    for engine in ("synth", "piper"):
        help_result = subprocess.run(base + [engine, "--help"],
                                     capture_output=True, text=True, check=True)
        assert "--lexicon" in help_result.stdout


def test_piper_receives_spoken_text_not_original(tmp_path, monkeypatch):
    from vacuum_voice_hub.piper_studio import synthesize_piper_workspace
    voice = tmp_path / "test.onnx"
    voice.write_bytes(b"LOCAL TEST VOICE")
    (tmp_path / "test.onnx.json").write_text(json.dumps({"language": {"code": "uk_UA"}}))
    p = glossary(tmp_path)
    received = []
    monkeypatch.setattr("vacuum_voice_hub.piper_studio.shutil.which", lambda _: "/local/piper")
    def fake_run(cmd, *, input, text, capture_output, check, timeout):
        received.append(input)
        filename = cmd[cmd.index("--output_file")+1]
        with wave.open(filename, "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(16000)
            audio.writeframes(b"\x00\x20" * 16000)
        return subprocess.CompletedProcess(cmd, 0)
    monkeypatch.setattr("vacuum_voice_hub.piper_studio.subprocess.run", fake_run)
    result = synthesize_piper_workspace("uk", MODEL, "phonetic_uk", "Translator",
        voice, output=tmp_path / "project", allow_synthetic=True, lexicon_path=p)
    assert result["pronunciation_lexicon_sha256"] == load_lexicon(p, "uk")["sha256"]
    assert any("прибирАння" in phrase for phrase in received)
    assert result["install_authorized"] is False
