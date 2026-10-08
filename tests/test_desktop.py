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
