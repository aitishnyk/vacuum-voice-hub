"""Session-authenticated UI wrappers for existing local recovery primitives."""
import re,secrets,shutil
from .paths import data_dir
from .creator import workspace_by_id,default_workspace,load_workspace,save_manifest
from .creator_recovery import create_backup,restore_backup

MAX_UI_BACKUP=32*1024*1024

def backup_file(identity):
    if not isinstance(identity,str) or not re.fullmatch('[a-f0-9]{24}',identity):
        raise ValueError('invalid backup identity')
    root=data_dir()/'creator-backups'
    if root.is_symlink():raise ValueError('symlinked backup directory refused')
    root.mkdir(exist_ok=True)
    path=root/(identity+'.zip')
    if path.is_symlink():raise ValueError('symlinked backup refused')
    return path

def backup_project(pack_id):
    identity=secrets.token_hex(12)
    result=create_backup(workspace_by_id(pack_id),backup_file(identity))
    return {'backup_id':identity,'install_authorized':False}

def restore_project(payload):
    if not 0<len(payload)<=MAX_UI_BACKUP:raise ValueError('UI restore accepts ZIP files up to 32 MiB; use CLI for larger backups')
    identity=secrets.token_hex(12);source=backup_file(identity)
    new_id='restored-'+secrets.token_hex(12);target=default_workspace(new_id)
    try:
        with source.open('xb') as stream:stream.write(payload)
        restore_backup(source,target)
        root,manifest=load_workspace(target)
        manifest['id']=new_id;manifest['name']+=' (Restored)'
        save_manifest(root,manifest)
    except Exception:
        if target.exists():shutil.rmtree(target)
        raise
    finally:
        source.unlink(missing_ok=True)
    return {'id':new_id,'recovery_verified':True,'original_workspace_modified':False,'install_authorized':False}
