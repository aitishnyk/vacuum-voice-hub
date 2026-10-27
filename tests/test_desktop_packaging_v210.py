"""Publishing must never bundle a codec that declares itself nonredistributable."""
import pytest
from scripts import build_desktop

@pytest.mark.parametrize('license_text',['configuration: --enable-nonfree','This binary is not legally redistributable.'])
def test_nonfree_codec_refused_before_pyinstaller(tmp_path,monkeypatch,license_text):
    codec=tmp_path/'ffmpeg';codec.write_bytes(b'fake')
    monkeypatch.setenv('VVH_FFMPEG',str(codec))
    monkeypatch.setattr(build_desktop.subprocess,'check_output',lambda *a,**k:license_text)
    with pytest.raises(SystemExit,match='nonredistributable'):build_desktop.main()

def test_standalone_packaging_entrypoint_smoke(tmp_path,monkeypatch):
    """PyInstaller runs desktop.py as __main__, without a package parent."""
    import json,runpy,sys,types
    from pathlib import Path
    import vacuum_voice_hub.demo as demo
    class Event:
        callback=None
        def __iadd__(self,callback):self.callback=callback;return self
    loaded=Event()
    window=types.SimpleNamespace(events=types.SimpleNamespace(loaded=loaded),destroy=lambda:None)
    webview=types.SimpleNamespace(create_window=lambda *a,**k:window,start=lambda **k:loaded.callback())
    monkeypatch.setitem(sys.modules,'webview',webview)
    monkeypatch.setattr(demo,'start_demo',lambda:{'id':'mock'})
    monkeypatch.setattr(demo,'process_demo',lambda *a:None)
    monkeypatch.setattr(demo,'export_demo',lambda *a:None)
    report=tmp_path/'smoke.json'
    monkeypatch.setattr(sys,'argv',['desktop.py','--smoke-test',str(report)])
    runpy.run_path(str(Path(__file__).resolve().parents[1]/'vacuum_voice_hub'/'desktop.py'),run_name='__main__')
    result=json.loads(report.read_text())
    assert result['gui_loaded'] and result['demo_e2e'] and result['server_closed']
    assert result['native_audible_playback_verified'] is False
