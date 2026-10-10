"""Safety regression for the localhost Creator Studio privacy boundary."""
from pathlib import Path
import json
import threading
import urllib.error
import urllib.request

import pytest

import vacuum_voice_hub.server as server


@pytest.fixture
def creator_http(monkeypatch):
    monkeypatch.setattr(server, "list_workspaces", lambda: [
        {"id": "private-voice", "name": "Sensitive local project",
         "path": "/private/voice", "events": 1, "ok": True}
    ])
    instance = server.make_server(0)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:" + str(instance.server_address[1])
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=5)


def request_json(base, path, headers=None, data=None):
    request = urllib.request.Request(base + path, headers=headers or {},
                                     data=data)
    try:
        with urllib.request.urlopen(request, timeout=5) as result:
            return result.status, json.load(result)
    except urllib.error.HTTPError as exc:
        return exc.code, json.load(exc)


@pytest.mark.parametrize("endpoint", [
    "/api/creator/workspaces",
    "/api/creator/workspace?id=private-voice",
    "/api/creator/preflight?id=private-voice",
    "/api/creator/qa?id=private-voice",
    "/api/creator/language-coverage?id=private-voice",
])
def test_private_creator_get_requires_session(creator_http, endpoint):
    status, payload = request_json(creator_http, endpoint)
    assert status == 403
    assert payload["ok"] is False
    assert "Sensitive local project" not in json.dumps(payload)


def test_private_creator_list_available_to_studio_session(creator_http):
    status, payload = request_json(creator_http, "/api/creator/workspaces",
                                    {"X-VVH-Session": server.CREATOR_SESSION})
    assert status == 200
    assert payload["workspaces"][0]["id"] == "private-voice"


def test_cross_site_origin_cannot_read_session(creator_http):
    status, payload = request_json(
        creator_http, "/api/session", {"Origin": "https://attacker.example"}
    )
    assert status == 403
    assert "creator_session" not in payload


def test_dns_rebinding_host_cannot_read_session(creator_http):
    status, payload = request_json(
        creator_http, "/api/session", {"Host": "malicious.example"}
    )
    assert status == 403
    assert "creator_session" not in payload


def test_cross_site_origin_cannot_post(creator_http):
    status, payload = request_json(
        creator_http, "/api/creator/new",
        {"Origin": "https://attacker.example", "Content-Type": "application/json"},
        data=b"{}"
    )
    assert status == 403
    assert payload["ok"] is False


def test_local_session_endpoint_remains_accessible(creator_http):
    status, payload = request_json(creator_http, "/api/session")
    assert status == 200
    assert payload["creator_session"] == server.CREATOR_SESSION


def test_creator_labels_are_encoded_as_dom_text_or_escaped():
    ui = (Path(server.__file__).parent / "web" / "creator.html").read_text("utf-8")
    assert "model.replaceChildren" in ui
    assert "category.replaceChildren" in ui
    assert "workspace.replaceChildren" in ui
    assert "escapeHtml(e.semantic)" in ui
    assert "escapeHtml(e.category)" in ui
    assert "escapeHtml(e.description||'Без описания')" in ui
    assert "escapeHtml(rel)" in ui
    assert "data-file=\"${escapeHtml(e.semantic)}\"" in ui
