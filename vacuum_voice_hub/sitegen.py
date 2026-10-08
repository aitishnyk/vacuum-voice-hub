import hashlib,json
from importlib.resources import files
from pathlib import Path
from . import __version__
from .catalog import voices,models,event_profiles

SCHEMA="vvh.public-catalog.v1"

def _write_json(path,obj):
    data=(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()

def _public_voice(v):
    return {
        "id":v["id"],
        "title":v["title"],
        "language":v["language"],
        "adult":bool(v.get("adult")),
        "content_rating":v.get("content_rating"),
        "tags":v.get("tags",[]),
        "credit":v.get("credit"),
        "origin_model":v.get("origin_model"),
        "format":v.get("format"),
        "source_verification":v.get("source_verification"),
        "source_page":v.get("source",{}).get("page"),
        "redistribution":v.get("redistribution"),
    }

def _public_model(m,profiles):
    p=profiles.get(m.get("event_profile"),{})
    t=m.get("transport",{})
    return {
        "id":m["id"],
        "name":m["name"],
        "vendor":m.get("vendor"),
        "aliases":m.get("aliases",[]),
        "device_tested":bool(m.get("device_tested")),
        "event_profile":m.get("event_profile"),
        "event_count":len(p.get("known_event_ids",[])),
        "profile_kind":p.get("profile_kind"),
        "profile_hardware_verified":bool(p.get("hardware_verified")),
        "transport_kind":t.get("kind"),
        "transport_verification":t.get("verification"),
        "install_default":bool(t.get("allow_default")),
        "notes":m.get("notes"),
        "adapter":m.get("adapter"),
        "package_container":(m.get("package") or {}).get("container"),
        "product_id":m.get("product_id"),
        "plugin_id":m.get("plugin_id"),
        "custom_install_policy":(
            "hardware-verified" if m.get("device_tested")
            else "experimental" if t.get("kind") in {"miot-local-property","roborock-miio-sound","miot-action-url-md5"}
            else "official-signed-only" if t.get("kind")=="signed-official-only"
            else "build-only"
        ),
    }

def build_site(output):
    out=Path(output).expanduser().resolve()
    out.mkdir(parents=True,exist_ok=True)
    profile_map={p["id"]:p for p in event_profiles()}
    vv=[_public_voice(v) for v in voices()]
    mm=[_public_model(m,profile_map) for m in models()]
    catalog={
        "schema":SCHEMA,
        "version":__version__,
        "voices":vv,
        "stats":{
            "voices":len(vv),
            "languages":sorted({v["language"] for v in vv}),
            "adult":sum(v["adult"] for v in vv),
        },
    }
    model_doc={
        "schema":SCHEMA,
        "version":__version__,
        "models":mm,
        "stats":{
            "models":len(mm),
            "hardware_verified":sum(m["device_tested"] for m in mm),
        },
    }
    hashes={
        "catalog.json":_write_json(out/"catalog.json",catalog),
        "models.json":_write_json(out/"models.json",model_doc),
    }
    manifest={
        "schema":SCHEMA,
        "version":__version__,
        "files":{name:{"sha256":digest} for name,digest in sorted(hashes.items())},
        "counts":{
            "voices":len(vv),
            "models":len(mm),
            "languages":len(catalog["stats"]["languages"]),
            "hardware_verified_models":model_doc["stats"]["hardware_verified"],
        },
    }
    manifest_hash=_write_json(out/"manifest.json",manifest)
    template=(files("vacuum_voice_hub")/"site"/"index.html").read_text(encoding="utf-8")
    (out/"index.html").write_text(template,encoding="utf-8")
    index_hash=hashlib.sha256((out/"index.html").read_bytes()).hexdigest()
    return {
        "output":str(out),
        "schema":SCHEMA,
        "version":__version__,
        "voices":len(vv),
        "models":len(mm),
        "hashes":{**hashes,"manifest.json":manifest_hash,"index.html":index_hash},
    }

def verify_site(path):
    root=Path(path).expanduser().resolve()
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    errors=[]
    if manifest.get("schema")!=SCHEMA:
        errors.append("manifest schema mismatch")
    for name,meta in manifest.get("files",{}).items():
        p=root/name
        if not p.is_file():
            errors.append(f"missing file: {name}")
            continue
        got=hashlib.sha256(p.read_bytes()).hexdigest()
        if got!=meta.get("sha256"):
            errors.append(f"sha256 mismatch: {name}")
    return {"ok":not errors,"errors":errors,"manifest":manifest}
