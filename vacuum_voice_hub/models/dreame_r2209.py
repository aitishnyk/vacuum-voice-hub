import hashlib, json, tarfile
from pathlib import Path
MODEL_ID="dreame.vacuum.r2209"

def package(canonical_dir: Path, out: Path) -> dict:
    files=sorted(canonical_dir.glob("*.ogg"), key=lambda p:int(p.stem))
    if len(files)<5: raise ValueError("too few canonical events")
    with tarfile.open(out,"w:gz") as tf:
        for f in files: tf.add(f,arcname=f.name,recursive=False)
    data=out.read_bytes()
    return {"path":out,"size":len(data),"md5":hashlib.md5(data).hexdigest(),"events":len(files)}

def make_voice_value(pack_id,url,md5,size):
    return json.dumps({"id":pack_id,"url":url,"md5":md5,"size":size},separators=(",",":"))
