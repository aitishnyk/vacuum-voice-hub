import hashlib,json,re,zipfile
from pathlib import Path
from ..audio import normalize
from ..catalog import event_by_id

OUTPUT_SUFFIX=".zip"

def _safe(s):
    s=re.sub(r"[^A-Za-z0-9._-]+","_",s or "event").strip("._")
    return s or "event"

def package(canonical_dir:Path,out:Path,allowed_ids=None)->dict:
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for src in sorted(Path(canonical_dir).glob("*.ogg"),key=lambda p:int(p.stem) if p.stem.isdigit() else 10**9):
            try:event_id=int(src.stem)
            except ValueError:continue
            if allowed_ids is not None and event_id not in allowed_ids:continue
            e=event_by_id(event_id);semantic=e.get("semantic") or f"event.{event_id}"
            name=f"audio/{event_id:03d}__{_safe(semantic)}.ogg"
            zf.write(src,arcname=name)
            rows.append({"id":event_id,"semantic":semantic,"category":e.get("category"),"file":name})
        if len(rows)<5:raise ValueError("too few portable semantic events")
        manifest={"schema":"vvh.portable-build.v1","installable":False,"events":rows,"note":"Model package/transport unverified. This bundle is for adaptation, review and preview; it is not a vendor-installable voice pack."}
        zf.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    data=out.read_bytes()
    return {"path":out,"size":len(data),"md5":hashlib.md5(data).hexdigest(),"events":len(rows),"event_ids":[x["id"] for x in rows],"installable":False}

def make_voice_value(pack_id,url,md5,size):
    raise RuntimeError("Portable semantic bundles are build-only and cannot be installed directly")
