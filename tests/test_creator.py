import json,math,struct,tarfile,wave
from pathlib import Path
import pytest
from vacuum_voice_hub.creator import (
    new_workspace,assign_audio,validate_workspace,workspace_model_coverage,
    build_workspace,update_manifest
)

def _wav(path:Path,freq=440):
    rate=16000
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
        frames=[]
        for i in range(rate//12):
            v=int(4500*math.sin(2*math.pi*freq*i/rate))
            frames.append(struct.pack("<h",v))
        w.writeframes(b"".join(frames))

def test_creator_new_validate_assign_and_build(tmp_path):
    root=tmp_path/"creator-pack"
    r=new_workspace(root,pack_id="test-pack",name="Test Pack",author="VVH Test",language="en",license_name="CC0-1.0")
    assert r["manifest"]["schema"]=="vvh.voicepack.v1"
    assert validate_workspace(root)["ok"] is False

    src=tmp_path/"sample.wav";_wav(src)
    semantics=["clean.start","clean.pause","clean.complete","error.main_brush","locate.here"]
    for i,semantic in enumerate(semantics):
        if i:_wav(src,440+i*20)
        assign_audio(root,semantic,src)

    v=validate_workspace(root)
    assert v["ok"] is True
    assert v["valid_events"]==5

    c=workspace_model_coverage(root,"dreame.vacuum.r2209")
    assert c["mapped_semantics"]==5
    assert set(c["mapped_event_ids"])=={7,11,12,35,45}

    out=tmp_path/"built.tar.gz"
    meta=build_workspace(root,"dreame.vacuum.r2209",out)
    assert meta["events"]==5
    assert out.is_file()
    with tarfile.open(out,"r:gz") as tf:
        assert set(tf.getnames())=={"7.ogg","11.ogg","12.ogg","35.ogg","45.ogg"}

def test_creator_manifest_validation_and_path_safety(tmp_path):
    root=tmp_path/"pack"
    new_workspace(root,pack_id="safe-pack",name="Safe",author="Author",language="ru")
    manifest=json.loads((root/"manifest.json").read_text())
    manifest["events"]={"clean.start":"../escape.wav"}
    (root/"manifest.json").write_text(json.dumps(manifest))
    v=validate_workspace(root)
    assert v["ok"] is False
    assert any("unsafe event path" in x for x in v["errors"])

def test_creator_metadata_update_reports_unlicensed_warning(tmp_path):
    root=tmp_path/"pack"
    new_workspace(root,pack_id="meta-pack",name="Meta",author="Author",language="uk")
    r=update_manifest(root,{"name":"Renamed","adult":True})
    assert r["manifest"]["name"]=="Renamed"
    assert r["manifest"]["adult"] is True
    assert any("UNLICENSED" in x for x in r["warnings"])

def test_creator_rejects_invalid_pack_id(tmp_path):
    with pytest.raises(ValueError):
        new_workspace(tmp_path/"bad",pack_id="../bad",name="Bad",author="A",language="en")
