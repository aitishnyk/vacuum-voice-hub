"""v0.21 bounded batch mastering with rollback and portability checks."""
import hashlib
import json
import math
import struct
import subprocess
import sys
import wave

import pytest

from vacuum_voice_hub.audio_batch import master_batch


def wav(path, amp=6000):
    rate = 16000
    samples = [0] * 2000
    samples += [round(amp * math.sin(2*math.pi*300*i/rate)) for i in range(rate)]
    samples += [0] * 2000
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        f.writeframes(struct.pack("<" + "h"*len(samples), *samples))


def test_batch_output_is_new_and_all_inputs_stay_untouched(tmp_path):
    inp=tmp_path/"input"; inp.mkdir()
    a=inp/"clean.start.wav"; b=inp/"clean.pause.wav"
    wav(a); wav(b,amp=7000)
    (inp/"README.md").write_text("not audio")
    h={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (a,b)}
    dest=tmp_path/"previews"
    result=master_batch(inp,dest,target_peak_dbfs=-6,padding_ms=30)
    assert result["schema"]=="vvh.master-batch.v1"
    assert result["clip_count"]==2
    assert set(p.name for p in dest.iterdir())=={
        "clean.start.wav", "clean.pause.wav", "batch-mastering.json"}
    manifest=json.loads((dest/"batch-mastering.json").read_text("utf-8"))
    assert manifest["input_count"]==2
    assert manifest["human_review_required"]
    assert manifest["redistribution_verified"] is False
    assert manifest["install_authorized"] is False
    assert [x["source_name"] for x in manifest["clips"]]==["clean.pause.wav","clean.start.wav"]
    for p in (a,b):
        assert hashlib.sha256(p.read_bytes()).hexdigest()==h[p.name]
    with pytest.raises(FileExistsError):
        master_batch(inp,dest)


def test_batch_fails_atomically_for_one_bad_recording(tmp_path):
    inp=tmp_path/"input"; inp.mkdir()
    wav(inp/"good.wav")
    wav(inp/"silent.wav",amp=0)
    out=tmp_path/"out"
    with pytest.raises(ValueError,match="no audio"):
        master_batch(inp,out)
    assert not out.exists()
    assert (inp/"good.wav").is_file()


def test_case_insensitive_and_extension_collision_fails_before_output(tmp_path):
    inp=tmp_path/"input";inp.mkdir()
    wav(inp/"alpha.wav")
    (inp/"ALPHA.mp3").write_bytes(b"fake")
    out=tmp_path/"new"
    with pytest.raises(ValueError, match="collide"):
        master_batch(inp,out)
    assert not out.exists()


def test_symlinked_audio_rejected_without_traversal(tmp_path):
    inp=tmp_path/"input";inp.mkdir()
    source=tmp_path/"source.wav";wav(source)
    (inp/"link.wav").symlink_to(source)
    with pytest.raises(ValueError,match="symlink"):
        master_batch(inp,tmp_path/"out")
    assert not (tmp_path/"out").exists()


def test_invalid_max_files_and_empty_batch(tmp_path):
    inp=tmp_path/"input";inp.mkdir()
    with pytest.raises(ValueError,match="1.."):
        master_batch(inp,tmp_path/"out")
    wav(inp/"a.wav")
    with pytest.raises(ValueError,match="max_files"):
        master_batch(inp,tmp_path/"out",max_files=0)
    with pytest.raises(ValueError,match="max_files"):
        master_batch(inp,tmp_path/"out",max_files=True)
    assert not (tmp_path/"out").exists()


def test_cli_exposes_batch_command():
    result=subprocess.run([sys.executable,"-m","vacuum_voice_hub",
                           "creator","master-batch","--help"],
                          capture_output=True,text=True,check=True)
    assert "--input-dir" in result.stdout
    assert "--output-dir" in result.stdout
    assert "--max-files" in result.stdout


def test_mastering_json_schemas_publish_non_authorizing_contracts():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / "schemas"
    a = json.loads((root / "vvh.master-preview.v1.schema.json").read_text("utf-8"))
    b = json.loads((root / "vvh.master-batch.v1.schema.json").read_text("utf-8"))
    assert a["properties"]["schema"]["const"] == "vvh.master-preview.v1"
    assert b["properties"]["schema"]["const"] == "vvh.master-batch.v1"
    assert b["properties"]["input_count"]["maximum"] == 256
    for contract in (a, b):
        for key, value in [("install_authorized", False),
                           ("redistribution_verified", False),
                           ("human_review_required", True),
                           ("creator_manifest_changed", False)]:
            assert contract["properties"][key]["const"] is value
