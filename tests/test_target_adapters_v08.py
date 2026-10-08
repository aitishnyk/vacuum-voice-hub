import math,struct,wave,zipfile,tarfile,shutil
from pathlib import Path
from vacuum_voice_hub.audio import normalize
from vacuum_voice_hub.models import roborock_legacy,ijai_zip,semantic_bundle
from vacuum_voice_hub.catalog import event_profile_for_model
from vacuum_voice_hub import miot

def _wav(path:Path,freq=440):
    rate=16000
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
        frames=[struct.pack("<h",int(4500*math.sin(2*math.pi*freq*i/rate))) for i in range(rate//20)]
        w.writeframes(b"".join(frames))

def _canonical(tmp_path,ids):
    src=tmp_path/"src.wav";_wav(src)
    out=tmp_path/"canonical";out.mkdir()
    for i,event_id in enumerate(ids):
        if i:_wav(src,440+i*15)
        normalize(src,out/f"{event_id}.ogg","ogg")
    return out

def test_ijai_zip_builder_uses_named_mp3(tmp_path):
    ids=event_profile_for_model("ijai.vacuum.v2")["known_event_ids"][:12]
    canonical=_canonical(tmp_path,ids)
    out=tmp_path/"voice.zip"
    meta=ijai_zip.package(canonical,out,allowed_ids=set(ids))
    assert meta["events"]>=5
    with zipfile.ZipFile(out) as zf:
        names=zf.namelist()
        assert all(n.endswith(".mp3") for n in names)
        assert any("sound_" in n for n in names)

def test_semantic_bundle_is_explicitly_non_installable(tmp_path):
    ids=event_profile_for_model("xiaomi.vacuum.d101")["known_event_ids"][:8]
    canonical=_canonical(tmp_path,ids)
    out=tmp_path/"portable.zip"
    meta=semantic_bundle.package(canonical,out,allowed_ids=set(ids))
    assert meta["installable"] is False
    with zipfile.ZipFile(out) as zf:
        assert "manifest.json" in zf.namelist()
        manifest=zf.read("manifest.json").decode()
        assert '"installable": false' in manifest

def test_roborock_builder_creates_named_wav_before_encrypt(tmp_path,monkeypatch):
    ids=[0,7,8,9,10,11,12,13,18,35,36,45]
    canonical=_canonical(tmp_path,ids)
    captured={}
    def fake_encrypt(src,dst):
        captured["src"]=Path(src)
        shutil.copyfile(src,dst)
        return dst
    monkeypatch.setattr(roborock_legacy,"encrypt_roborock_pkg",fake_encrypt)
    out=tmp_path/"voice.pkg"
    meta=roborock_legacy.package(canonical,out,allowed_ids=set(ids))
    assert meta["events"]>=5
    assert out.is_file()
    assert tarfile.is_tarfile(out)
    with tarfile.open(out,"r:gz") as tf:
        names=set(tf.getnames())
        assert "start.wav" in names
        assert "pause.wav" in names
        assert "finish.wav" in names

class FakeDevice:
    def __init__(self,responses=None):
        self.calls=[];self.responses=responses or {}
    def send(self,command,payload=None):
        self.calls.append((command,payload))
        return self.responses.get(command,[{"code":0}])

def test_roborock_and_ijai_transport_payloads(monkeypatch):
    d=FakeDevice({"get_sound_progress":[{"sid":123,"progress":100}]})
    monkeypatch.setattr(miot,"device",lambda ip,token:d)
    r=miot.set_voice("1.2.3.4","a"*32,{"url":"http://x/a.pkg","md5":"abc","sid":123},{
        "kind":"roborock-miio-sound",
    })
    assert d.calls[-1][0]=="dnld_install_sound"
    st=miot.voice_status("1.2.3.4","a"*32,{"kind":"roborock-miio-sound"})
    assert st["state"]=="success" and st["progress"]==100

    d2=FakeDevice()
    monkeypatch.setattr(miot,"device",lambda ip,token:d2)
    miot.set_voice("1.2.3.4","a"*32,{"language":"ru_RU","url":"http://x/a.zip","md5":"def"},{
        "kind":"miot-action-url-md5","command":"ijai.vacuum.v2.action",
        "siid":14,"aiid":1,"language_piid":1,"url_piid":5,"md5_piid":6,
    })
    cmd,payload=d2.calls[-1]
    assert cmd=="ijai.vacuum.v2.action"
    assert payload["siid"]==14 and payload["aiid"]==1
    assert [x["piid"] for x in payload["in"]]==[1,5,6]
