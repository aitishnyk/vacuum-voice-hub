import json,re,tempfile
from pathlib import Path
from .audio import normalize
from .catalog import events,event_profile_for_model,model_by_id,event_by_semantic
from .models.registry import get as get_model
from .paths import creator_dir

SCHEMA="vvh.voicepack.v1"
PACK_ID_RE=re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")
LANG_RE=re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]+)*$")
AUDIO_SUFFIXES={".wav",".mp3",".ogg",".m4a",".aac",".flac",".opus"}
MAX_AUDIO_BYTES=25*1024*1024

def _safe_relative(path_text):
    p=Path(path_text)
    return (not p.is_absolute()) and ".." not in p.parts and len(p.parts)>0

def _workspace(path):
    return Path(path).expanduser().resolve()

def default_workspace(pack_id):
    if not PACK_ID_RE.fullmatch(pack_id):
        raise ValueError("invalid creator workspace id")
    root=(creator_dir()/pack_id).resolve()
    root.relative_to(creator_dir().resolve())
    return root

def workspace_by_id(pack_id):
    return default_workspace(pack_id)

def new_workspace(path=None,*,pack_id,name,author,language,adult=False,license_name="UNLICENSED",source_url=None,description=None):
    if not PACK_ID_RE.fullmatch(pack_id):
        raise ValueError("pack id must match ^[a-z0-9][a-z0-9._-]{1,63}$")
    if not LANG_RE.fullmatch(language):
        raise ValueError("invalid language code")
    root=_workspace(path or default_workspace(pack_id))
    root.mkdir(parents=True,exist_ok=True)
    (root/"audio").mkdir(exist_ok=True)
    manifest_path=root/"manifest.json"
    if manifest_path.exists():
        raise FileExistsError(f"manifest already exists: {manifest_path}")
    manifest={
        "schema":SCHEMA,
        "id":pack_id,
        "name":name.strip(),
        "author":author.strip(),
        "language":language,
        "adult":bool(adult),
        "license":license_name.strip() or "UNLICENSED",
        "source_url":source_url,
        "description":description,
        "events":{},
    }
    save_manifest(root,manifest)
    return {"workspace":str(root),"manifest":manifest}

def load_workspace(path):
    root=_workspace(path)
    manifest_path=root/"manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest.json not found in {root}")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    return root,manifest

def save_manifest(root,manifest):
    root=Path(root)
    (root/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def update_manifest(path,updates):
    root,manifest=load_workspace(path)
    allowed={"name","author","language","adult","license","source_url","description"}
    for key,value in updates.items():
        if key not in allowed:
            continue
        manifest[key]=value
    save_manifest(root,manifest)
    return validate_workspace(root)

def _semantic_known(semantic):
    return any(e.get("semantic")==semantic for e in events())

def assign_audio(path,semantic,source_file,copy=True):
    root,manifest=load_workspace(path)
    if not _semantic_known(semantic):
        raise ValueError(f"unknown semantic event: {semantic}")
    src=Path(source_file).expanduser().resolve()
    if not src.is_file():
        raise FileNotFoundError(src)
    if src.stat().st_size>MAX_AUDIO_BYTES:
        raise ValueError("audio file exceeds 25 MiB creator limit")
    if src.suffix.lower() not in AUDIO_SUFFIXES:
        raise ValueError(f"unsupported audio extension: {src.suffix}")
    safe_name=f"{semantic.replace('/','_')}{src.suffix.lower()}"
    dst=root/"audio"/safe_name
    if copy:
        dst.write_bytes(src.read_bytes())
        rel=f"audio/{safe_name}"
    else:
        try:
            rel=str(src.relative_to(root))
        except ValueError:
            raise ValueError("non-copy mode requires source inside workspace")
    manifest["events"][semantic]=rel
    save_manifest(root,manifest)
    return {"workspace":str(root),"semantic":semantic,"path":rel}

def assign_audio_bytes(path,semantic,filename,data):
    if len(data)>MAX_AUDIO_BYTES:
        raise ValueError("audio upload exceeds 25 MiB creator limit")
    suffix=Path(filename or "").suffix.lower()
    if suffix not in AUDIO_SUFFIXES:
        raise ValueError(f"unsupported audio extension: {suffix or '(none)'}")
    root,_=load_workspace(path)
    temp=root/"audio"/("_upload"+suffix)
    temp.write_bytes(data)
    try:
        return assign_audio(root,semantic,temp,copy=True)
    finally:
        temp.unlink(missing_ok=True)

def remove_event(path,semantic):
    root,manifest=load_workspace(path)
    rel=manifest.get("events",{}).pop(semantic,None)
    save_manifest(root,manifest)
    return {"removed":semantic,"path":rel}

def validate_workspace(path):
    root,manifest=load_workspace(path)
    errors=[];warnings=[]
    required=["schema","id","name","author","language","adult","license","events"]
    for key in required:
        if key not in manifest:
            errors.append(f"missing required field: {key}")
    if manifest.get("schema")!=SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if not PACK_ID_RE.fullmatch(str(manifest.get("id",""))):
        errors.append("invalid id")
    if not str(manifest.get("name","")).strip():
        errors.append("name is empty")
    if not str(manifest.get("author","")).strip():
        errors.append("author is empty")
    if not LANG_RE.fullmatch(str(manifest.get("language",""))):
        errors.append("invalid language")
    if not isinstance(manifest.get("adult"),bool):
        errors.append("adult must be boolean")
    if not str(manifest.get("license","")).strip():
        errors.append("license is empty")
    if str(manifest.get("license","")).upper()=="UNLICENSED":
        warnings.append("license is UNLICENSED; keep redistribution private unless rights are clarified")
    event_map=manifest.get("events",{})
    if not isinstance(event_map,dict) or not event_map:
        errors.append("events must contain at least one semantic audio mapping")
    known={e["semantic"] for e in events()}
    seen_paths=set();valid_events=0
    for semantic,rel in event_map.items() if isinstance(event_map,dict) else []:
        if semantic not in known:
            errors.append(f"unknown semantic event: {semantic}")
        if not isinstance(rel,str) or not _safe_relative(rel):
            errors.append(f"unsafe event path for {semantic}: {rel!r}")
            continue
        f=(root/rel).resolve()
        try:
            f.relative_to(root)
        except ValueError:
            errors.append(f"event path escapes workspace: {rel}")
            continue
        if not f.is_file():
            errors.append(f"missing audio file for {semantic}: {rel}")
            continue
        if f.suffix.lower() not in AUDIO_SUFFIXES:
            errors.append(f"unsupported audio format for {semantic}: {f.suffix}")
            continue
        if rel in seen_paths:
            warnings.append(f"audio file reused by multiple events: {rel}")
        seen_paths.add(rel);valid_events+=1
    return {
        "ok":not errors,
        "workspace":str(root),
        "manifest":manifest,
        "valid_events":valid_events,
        "errors":errors,
        "warnings":warnings,
    }

def workspace_model_coverage(path,model_id):
    validation=validate_workspace(path)
    model=model_by_id(model_id)
    profile=event_profile_for_model(model["id"])
    known_ids=set(profile["known_event_ids"])
    mapped={};unmapped=[]
    for semantic in validation["manifest"].get("events",{}):
        ids=sorted({int(e["id"]) for e in event_by_semantic(semantic) if int(e["id"]) in known_ids})
        if ids:
            mapped[semantic]=ids
        else:
            unmapped.append(semantic)
    produced_ids=sorted({x for ids in mapped.values() for x in ids})
    return {
        "model_id":model["id"],
        "profile":profile["id"],
        "profile_events":len(known_ids),
        "semantic_events":len(validation["manifest"].get("events",{})),
        "mapped_semantics":len(mapped),
        "mapped_event_ids":produced_ids,
        "mapped_event_count":len(produced_ids),
        "unmapped_semantics":sorted(unmapped),
        "coverage_pct":round(len(produced_ids)/len(known_ids)*100,1) if known_ids else 0.0,
    }

def workspace_snapshot(path,model_id=None):
    validation=validate_workspace(path)
    out={"validation":validation}
    if model_id:
        out["coverage"]=workspace_model_coverage(path,model_id)
    return out

def build_workspace(path,model_id,output=None):
    validation=validate_workspace(path)
    if not validation["ok"]:
        raise ValueError("invalid workspace: "+"; ".join(validation["errors"]))
    root=Path(validation["workspace"]);manifest=validation["manifest"]
    model=model_by_id(model_id);profile=event_profile_for_model(model["id"])
    known_ids=set(profile["known_event_ids"])
    with tempfile.TemporaryDirectory(prefix="vvh-creator-") as td:
        canonical=Path(td)/"canonical";canonical.mkdir()
        semantic_to_ids={}
        for semantic,rel in manifest["events"].items():
            ids=sorted({int(e["id"]) for e in event_by_semantic(semantic) if int(e["id"]) in known_ids})
            if not ids:
                continue
            semantic_to_ids[semantic]=ids
            src=root/rel
            normalized=Path(td)/"normalized"/(semantic.replace("/","_")+".ogg")
            normalize(src,normalized,"ogg")
            payload=normalized.read_bytes()
            for event_id in ids:
                (canonical/f"{event_id}.ogg").write_bytes(payload)
        if len(list(canonical.glob("*.ogg")))<5:
            raise ValueError("fewer than 5 target-model events were mapped; add more semantic events before building")
        adapter=get_model(model["id"])
        suffix=getattr(adapter,"OUTPUT_SUFFIX",".tar.gz")
        out=Path(output).expanduser().resolve() if output else root/f"{manifest['id']}__{model['id'].replace('.','_')}{suffix}"
        meta=adapter.package(canonical,out,allowed_ids=known_ids)
    return {
        **meta,
        "workspace":str(root),
        "pack_id":manifest["id"],
        "pack_name":manifest["name"],
        "author":manifest["author"],
        "model_id":model["id"],
        "target_adapter":model.get("adapter"),
        "output_suffix":getattr(get_model(model["id"]),"OUTPUT_SUFFIX",".tar.gz"),
        "semantic_mappings":semantic_to_ids,
        "coverage":workspace_model_coverage(root,model["id"]),
    }

def list_workspaces():
    out=[]
    for p in creator_dir().iterdir():
        if not p.is_dir() or not (p/"manifest.json").is_file():
            continue
        try:
            v=validate_workspace(p)
            out.append({"id":v["manifest"].get("id"),"name":v["manifest"].get("name"),"path":str(p),"ok":v["ok"],"events":len(v["manifest"].get("events",{}))})
        except Exception as e:
            out.append({"id":p.name,"name":p.name,"path":str(p),"ok":False,"error":str(e)})
    return sorted(out,key=lambda x:(x.get("name") or "").lower())
