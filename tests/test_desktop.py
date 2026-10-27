from vacuum_voice_hub.server import make_server
import vacuum_voice_hub.desktop as desktop

def test_server_can_bind_ephemeral_localhost_port():
    srv=make_server(0)
    try:
        host,port=srv.server_address[:2]
        assert host=="127.0.0.1"
        assert int(port)>0
    finally:
        srv.server_close()

def test_desktop_module_imports_without_pywebview_at_import_time():
    assert callable(desktop.main)

def test_loopback_startup_does_not_resolve_dns(monkeypatch):
    import socket
    def unexpected_lookup(*args):
        raise AssertionError('fixed loopback server must not perform reverse DNS')
    monkeypatch.setattr(socket,'getfqdn',unexpected_lookup)
    server=make_server(0)
    try:
        assert server.server_address[0]=='127.0.0.1'
        assert server.server_name=='localhost'
        assert server.server_port>0
    finally:
        server.server_close()
