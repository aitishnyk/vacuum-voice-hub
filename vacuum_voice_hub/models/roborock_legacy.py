import hashlib, tarfile, tempfile, zlib
from pathlib import Path
from ..audio import normalize
from ..catalog import roborock_map
from ..legacy_ccrypt import encrypt_roborock_pkg

OUTPUT_SUFFIX=".pkg"

def package(canonical_dir: Path,out: Path,allowed_ids=None)->dict:
    mapping=roborock_map()
    chosen={}
    for event_text,name in mapping.items():
        event_id=int(event_text)
        if allowed_ids is not None and event_id not in allowed_ids:continue
        src=Path(canonical_dir)/f"{event_id}.ogg"
        if not src.is_file():continue
        chosen.setdefault(name,src)
    if len(chosen)<5:
        raise ValueError("too few compatible Roborock semantic events")
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vvh-roborock-") as td:
        td=Path(td);wav=td/"wav";wav.mkdir()
        for name,src in sorted(chosen.items()):
            normalize(src,wav/name,"wav")
        archive=td/"voice.tar.gz"
        with tarfile.open(archive,"w:gz") as tf:
            for p in sorted(wav.iterdir(),key=lambda p:p.name):
                tf.add(p,arcname=p.name,recursive=False)
        encrypt_roborock_pkg(archive,out)
    data=out.read_bytes()
    return {
        "path":out,"size":len(data),"md5":hashlib.md5(data).hexdigest(),
        "events":len(chosen),"event_names":sorted(chosen),
        "requires_external":["ccrypt"],
    }

def make_voice_value(pack_id,url,md5,size):
    sid=10000+(zlib.crc32(pack_id.encode("utf-8"))%8000)
    return {"url":url,"md5":md5,"sid":sid,"size":int(size)}
