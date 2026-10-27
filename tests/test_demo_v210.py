"""Offline demo acceptance, isolation and failure safety."""
import hashlib,json,shutil,tarfile,threading,urllib.request,urllib.error
from pathlib import Path
from unittest.mock import patch
import pytest
from vacuum_voice_hub import demo
from vacuum_voice_hub.server import make_server,CREATOR_SESSION

@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.setenv('VVH_DATA_DIR',str(tmp_path/'data'))

def test_asset_audit():
    doc=demo.audit_assets()
    assert len(doc['events'])==8
    assert doc['license']=='CC0-1.0'

def test_demo_end_to_end_and_repeat():
    first=demo.start_demo();second=demo.start_demo()
    assert first['id']!=second['id']
    source=demo.demo_file(first['id'],'originals/01.wav')
    original=source.read_bytes()
    a=demo.process_demo(first['id'],'01.wav',-6)
    b=demo.process_demo(first['id'],'01.wav',-9)
    assert a['file']!=b['file']
    assert a['timeline']['bin_count']>0
    assert source.read_bytes()==original
    export=demo.export_demo(first['id'])
    path=demo.demo_file(first['id'],export['file'])
    assert hashlib.sha256(path.read_bytes()).hexdigest()==export['sha256']
    with tarfile.open(path) as archive:
        assert len(archive.getmembers())>=5
    assert not export['install_authorized']
    assert demo.export_demo(first['id'])['file']!=export['file']
    copied=demo.copy_to_creator(first['id'])
    from vacuum_voice_hub.creator import load_workspace,default_workspace
    assert load_workspace(default_workspace(copied['id']))[1]['language']=='en'
    shutil.rmtree(demo.session_root(first['id']))
    assert demo.start_demo()['id']!=first['id']

@pytest.mark.parametrize('path',['../manifest.json','originals/../../secret','/etc/passwd','processed/../manifest.json'])
def test_no_path_escape(path):
    started=demo.start_demo()
    with pytest.raises(ValueError):demo.demo_file(started['id'],path)

def test_no_symlink_reads(tmp_path):
    started=demo.start_demo();root=demo.session_root(started['id'])
    source=root/'originals'/'01.wav';source.unlink();source.symlink_to(tmp_path/'private.wav')
    with pytest.raises(ValueError):demo.demo_file(started['id'],'originals/01.wav')

def test_missing_and_corrupt_assets(tmp_path):
    shutil.copytree(demo.assets(),tmp_path/'assets')
    with patch.object(demo,'assets',return_value=tmp_path/'assets'):
        (tmp_path/'assets'/'01.wav').unlink()
        with pytest.raises(FileNotFoundError):demo.start_demo()
        (tmp_path/'assets'/'01.wav').write_bytes(b'broken')
        with pytest.raises(ValueError):demo.start_demo()

def test_decode_failure_and_disk_full_preserve_source():
    started=demo.start_demo();source=demo.demo_file(started['id'],'originals/01.wav');raw=source.read_bytes()
    with patch('vacuum_voice_hub.audio_mastering._decode',side_effect=ValueError('decode failed')):
        with pytest.raises(ValueError):demo.process_demo(started['id'],'01.wav')
    with patch.object(demo,'master_preview',side_effect=OSError('disk full')):
        with pytest.raises(OSError):demo.process_demo(started['id'],'01.wav')
    assert source.read_bytes()==raw
    assert not list((source.parent.parent/'processed').iterdir())

def test_api_auth_origin_and_demo():
    server=make_server(0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base='http://127.0.0.1:'+str(server.server_port)
    def request(route,data=None,token=CREATOR_SESSION,origin=None):
        headers={'X-VVH-Session':token,'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        return urllib.request.urlopen(urllib.request.Request(base+route,data=json.dumps(data).encode() if data is not None else None,headers=headers))
    try:
        for token,origin in [('bad',None),(CREATOR_SESSION,'https://evil.example')]:
            with pytest.raises(urllib.error.HTTPError) as exc:request('/api/demo/start',{},token,origin)
            assert exc.value.code==403
        started=json.load(request('/api/demo/start',{}))
        assert started['ok']
        processed=json.load(request('/api/demo/process',{'id':started['id'],'semantic':'01.wav','peak':-6}))
        assert processed['ok']
        assert json.load(request('/api/demo/export',{'id':started['id']}))['ok']
        assert b'Try Demo' in request('/').read()
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)
