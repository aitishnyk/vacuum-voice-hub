"""Real local HTTP integration for Universal Studio (auth and read-only QA)."""
import json
import threading
import urllib.error
import urllib.parse
import urllib.request
import wave

import pytest

from vacuum_voice_hub.creator import new_workspace, assign_audio
import vacuum_voice_hub.server as server


def test_local_studio_web_panel_and_auth(tmp_path, monkeypatch):
    root = tmp_path / "owned"
    new_workspace(root, pack_id="web_studio", name="Web studio",
                  author="Contributor", language="en", license_name="UNLICENSED")
    sound = tmp_path / "audio.wav"
    with wave.open(str(sound), "wb") as stream:
        stream.setnchannels(1);stream.setsampwidth(2);stream.setframerate(16000)
        stream.writeframes(b"\x00\x20" * 16000)
    assign_audio(root, "clean.start", sound)
    monkeypatch.setattr(server, "workspace_by_id", lambda pack: root if pack == "web_studio" else None)
    assert 'id="studioInspect"' in server.CREATOR_HTML
    assert "/api/studio/inspect" in server.CREATOR_HTML
    instance = server.make_server(0)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        query = urllib.parse.urlencode({
            "id": "web_studio", "model_id": "dreame.vacuum.r2209",
            "language": "en", "check_audio": "false",
        })
        uri = "http://127.0.0.1:" + str(instance.server_address[1]) + "/api/studio/inspect?" + query
        with pytest.raises(urllib.error.HTTPError) as denied:
            urllib.request.urlopen(uri, timeout=5)
        assert denied.value.code == 403
        request = urllib.request.Request(uri, headers={"X-VVH-Session": server.CREATOR_SESSION})
        with urllib.request.urlopen(request, timeout=10) as connection:
            payload = json.load(connection)
        assert payload["ok"] is True
        assert payload["report"]["schema"] == "vvh.universal-studio.v1"
        assert payload["report"]["pack_id"] == "web_studio"
        assert payload["report"]["hardware_install_authorized"] is False
        assert str(tmp_path) not in json.dumps(payload)
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=5)
