import shutil, subprocess, tempfile, tarfile, zipfile, re
from pathlib import Path
from .archive import extract
from .audio import normalize
from .catalog import bridge, ijai_map
from .formats.roborock_named import adapt_dir as adapt_roborock
from .formats.ijai_named_mp3 import adapt as adapt_ijai_archive
from .formats.robovoice_r2567r_mp3 import adapt as adapt_rv_archive
from .formats.dreame_canonical_ogg import adapt as adapt_ogg_archive
from .models.registry import get as get_model

def _ccrypt_decrypt(src: Path, dst: Path):
    exe=shutil.which('ccrypt') or shutil.which('ccat')
    if not exe: raise RuntimeError('Old Roborock .pkg import requires ccrypt. macOS: brew install ccrypt')
    if Path(exe).name=='ccat': cmd=[exe,'-k','-',str(src)]
    else: cmd=[exe,'-c','-k','-',str(src)]
    with open(dst,'wb') as f:
        p=subprocess.run(cmd,input='r0ckrobo#23456\n',text=True,stdout=f,stderr=subprocess.PIPE)
    if p.returncode: raise RuntimeError('ccrypt failed: '+p.stderr.strip())
    if not tarfile.is_tarfile(dst): raise ValueError('decrypted .pkg is not a tar archive')

def _adapt_dir(raw: Path, work: Path, fmt='auto'):
    out=work/'canonical'; out.mkdir(parents=True,exist_ok=True)
    names=[f.name for f in raw.rglob('*') if f.is_file()]
    if fmt in ('auto','dreame-canonical-ogg') and sum(bool(re.fullmatch(r'\d+\.ogg',n)) for n in names)>=5:
        found={}
        for f in raw.rglob('*.ogg'):
            if re.fullmatch(r'\d+\.ogg',f.name): found.setdefault(f.name,f)
        for name,src in found.items(): normalize(src,out/name,'ogg')
        return {'dir':out,'events':len(found),'detected':'dreame-canonical-ogg'}
    if fmt in ('auto','ijai-named-mp3') and sum('sound_' in n and n.endswith('.mp3') for n in names)>=5:
        files={f.name:f for f in raw.rglob('*.mp3')}; b=bridge(); used=[]
        for rid,name in ijai_map().items():
            if name not in files or rid not in b: continue
            dst=out/f"{int(b[rid])}.ogg"
            if dst.exists(): continue
            normalize(files[name],dst,'ogg'); used.append(name)
        if len(used)>=5: return {'dir':out,'events':len(used),'detected':'ijai-named-mp3'}
    if fmt in ('auto','robovoice-r2567r-mp3') and sum(bool(re.fullmatch(r'\d{3}\.mp3',n)) for n in names)>=5:
        files={f.name:f for f in raw.rglob('*.mp3')}; b=bridge(); used=[]
        for rid,target in b.items():
            src=files.get(f'{int(rid):03d}.mp3')
            if not src: continue
            dst=out/f"{int(target)}.ogg"
            if dst.exists(): continue
            normalize(src,dst,'ogg'); used.append(rid)
        if len(used)>=5: return {'dir':out,'events':len(used),'detected':'robovoice-r2567r-mp3'}
    if fmt in ('auto','roborock-named'):
        try:
            r=adapt_roborock(raw,out); r['detected']='roborock-named'; return r
        except ValueError:
            if fmt!='auto': raise
    raise ValueError('Could not detect local pack layout. Use --format explicitly or add an adapter.')

def convert_local(path, model_id='dreame.vacuum.r2209', fmt='auto', output=None):
    src=Path(path).expanduser().resolve()
    if not src.exists(): raise FileNotFoundError(src)
    with tempfile.TemporaryDirectory(prefix='vvh-import-') as td:
        work=Path(td); raw=work/'raw'; raw.mkdir()
        if src.is_dir():
            shutil.copytree(src,raw,dirs_exist_ok=True)
        elif src.suffix.lower()=='.pkg':
            dec=work/'decrypted.tar.gz'; _ccrypt_decrypt(src,dec); extract(dec,raw)
        else:
            extract(src,raw)
        adapted=_adapt_dir(raw,work,fmt)
        out=Path(output).expanduser().resolve() if output else src.parent/f'{src.stem}__{model_id.replace(".","_")}.tar.gz'
        meta=get_model(model_id).package(adapted['dir'],out)
        return {**meta,'detected':adapted.get('detected'),'output':str(out)}
