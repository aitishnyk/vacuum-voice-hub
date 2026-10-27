import pytest
from vacuum_voice_hub.demo import start_demo,copy_to_creator
from vacuum_voice_hub.project_actions import backup_project,backup_file,restore_project
from vacuum_voice_hub.creator import load_workspace,workspace_by_id

def test_ui_backup_restore_new_only(tmp_path,monkeypatch):
    monkeypatch.setenv('VVH_DATA_DIR',str(tmp_path))
    original=copy_to_creator(start_demo()['id'])['id']
    before=load_workspace(workspace_by_id(original))[1]
    backup=backup_project(original)
    data=backup_file(backup['backup_id']).read_bytes()
    restored=restore_project(data)
    again=restore_project(data)
    assert original!=restored['id']!=again['id']
    assert load_workspace(workspace_by_id(original))[1]==before
    after=load_workspace(workspace_by_id(restored['id']))[1]
    assert after['events']==before['events']
    with pytest.raises(Exception):restore_project(b'bad backup')
    assert load_workspace(workspace_by_id(original))[1]==before

def test_failed_manifest_replace_preserves_project(tmp_path,monkeypatch):
    from vacuum_voice_hub.creator import save_manifest,new_workspace
    import vacuum_voice_hub.creator as creator
    root=tmp_path/'project'
    new_workspace(root,pack_id='sample-project',name='Original',author='VVH',language='en')
    original=(root/'manifest.json').read_bytes()
    manifest=load_workspace(root)[1];manifest['name']='Unsaved change'
    def disk_full(*args):raise OSError('disk full')
    monkeypatch.setattr(creator.os,'replace',disk_full)
    with pytest.raises(OSError):save_manifest(root,manifest)
    assert (root/'manifest.json').read_bytes()==original
    assert not list(root.glob('.manifest-*'))
