import hashlib, zipfile
from pathlib import Path
from ..audio import normalize
from ..catalog import bridge,ijai_map

OUTPUT_SUFFIX=".zip"

def _canonical_to_name():
    b=bridge();names=ijai_map();out={}
    for rid,name in names.items():
        target=b.get(str(rid),b.get(rid))
        if target is None:continue
        out.setdefault(int(target),name)
    return out

def package(canonical_dir:Path,out:Path,allowed_ids=None)->dict:
    mapping=_canonical_to_name()
    selected=[]
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    temp=out.parent/(out.name+".work")
    if temp.exists():
        import shutil;shutil.rmtree(temp)
    temp.mkdir(parents=True)
    try:
        for event_id,name in sorted(mapping.items()):
            if allowed_ids is not None and event_id not in allowed_ids:continue
            src=Path(canonical_dir)/f"{event_id}.ogg"
            if not src.is_file():continue
            dst=temp/name
            normalize(src,dst,"mp3")
            selected.append((event_id,name))
        if len(selected)<5:raise ValueError("too few compatible IJAI events")
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
            for _,name in selected:zf.write(temp/name,arcname=name)
    finally:
        import shutil;shutil.rmtree(temp,ignore_errors=True)
    data=out.read_bytes()
    return {"path":out,"size":len(data),"md5":hashlib.md5(data).hexdigest(),"events":len(selected),"event_ids":[x[0] for x in selected],"event_names":[x[1] for x in selected]}

def make_voice_value(pack_id,url,md5,size):
    return {"language":"ru_RU","url":url,"md5":md5,"size":int(size)}
