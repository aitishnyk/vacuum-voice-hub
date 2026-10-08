import json
from pathlib import Path
from vacuum_voice_hub import history,report

def test_history_redacts_network_and_secret_data(tmp_path,monkeypatch):
    monkeypatch.setenv("VVH_DATA_DIR",str(tmp_path))
    token="a"*32
    row=history.append_history({
        "ok":True,
        "model_id":"dreame.vacuum.r2209",
        "token":token,
        "ip":"192.168.1.9",
        "mac":"AA:BB:CC:DD:EE:FF",
        "url":"http://192.168.1.9:8765/pack.tar.gz",
        "message":f"token={token} from 192.168.1.9",
    })
    raw=(tmp_path/"install-history.jsonl").read_text()
    assert token not in raw
    assert "192.168.1.9" not in raw
    assert "AA:BB:CC:DD:EE:FF" not in raw
    assert "token" not in row
    assert "ip" not in row
    assert row["message"]=="token=[redacted-token] from [redacted-ip]"

def test_compat_report_is_privacy_safe_and_candidate(tmp_path,monkeypatch):
    monkeypatch.setenv("VVH_DATA_DIR",str(tmp_path))
    monkeypatch.setattr(report.miot,"info",lambda ip,token:{
        "model":"dreame.vacuum.r2209",
        "firmware":"4.3.9_1321",
        "hardware":"Linux",
        "mac":"11:22:33:44:55:66",
    })
    monkeypatch.setattr(report.miot,"voice_status",lambda ip,token,transport:{
        "voice_id":"LBMAX","state":"success","progress":100,
    })
    monkeypatch.setattr(report,"latest_for_model",lambda model_id:{
        "ok":True,
        "action":"install",
        "voice_id":"maxim-full",
        "model_id":"dreame.vacuum.r2209",
        "robot_download_confirmed":True,
        "status":{"state":"success","progress":100},
    })
    built=report.build_report("192.168.0.106","b"*32,"dreame.vacuum.r2209")
    assert built["schema"]=="vvh.compat-report.v1"
    assert built["hardware_evidence_candidate"] is True
    assert "mac" not in built["device"]
    raw=json.dumps(built)
    assert "192.168.0.106" not in raw
    assert "b"*32 not in raw
    check=report.validate_report(built)
    assert check["ok"] is True
    out=report.write_report(built,tmp_path/"report.json")
    assert Path(out["path"]).is_file()
    assert len(out["sha256"])==64

def test_report_validator_rejects_forbidden_fields_and_values():
    bad={
        "schema":"vvh.compat-report.v1",
        "token":"c"*32,
        "device":{"model":"x","ip":"10.0.0.2"},
    }
    v=report.validate_report(bad)
    assert v["ok"] is False
    assert any("forbidden key" in e for e in v["errors"])
