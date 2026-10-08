import argparse,getpass,json
from .catalog import voices,models,voice_by_id,backlog,model_by_id,categories,events,event_profile_for_model
from .build import build_voice
from .install import install_voice
from .server import serve
from .stock import list_stock,install_stock
from .preview import preview_file
from .local_import import convert_local
from .creator import (
    new_workspace,validate_workspace,assign_audio,remove_event,
    workspace_model_coverage,build_workspace,list_workspaces
)
from .history import load_history
from .report import build_report,write_report,validate_report
from .sitegen import build_site,verify_site
from .release import build_release,verify_release
from . import credentials,miot,__version__

def _dump(x):
    print(json.dumps(x,ensure_ascii=False,indent=2,default=str))

def _resolve_token(a):
    direct=getattr(a,"token",None)
    credential=getattr(a,"credential",None)
    if direct and credential:
        raise SystemExit("Use either --token or --credential, not both")
    if credential:
        return credentials.load(credential)
    if direct:
        return direct
    return getpass.getpass("TOKEN (32 hex, hidden): ").strip()

def _add_auth_args(s):
    s.add_argument("--token")
    s.add_argument("--credential",help="Read token from OS Keychain/Secret Service")

def _parse_category_fallbacks(values):
    out={};valid=set(categories())
    for raw in values or []:
        if "=" not in raw:
            raise SystemExit(f"--fallback-category expects CATEGORY=VOICE, got {raw!r}")
        category,voice_id=raw.split("=",1)
        category=category.strip();voice_id=voice_id.strip()
        if category not in valid:
            raise SystemExit(f"Unknown category {category!r}. Valid: {', '.join(sorted(valid))}")
        if not voice_id:
            raise SystemExit(f"Missing voice id for fallback category {category}")
        out[category]=voice_id
    return out

def _add_build_args(s):
    s.add_argument("voice_id")
    s.add_argument("--model",default="dreame.vacuum.r2209")
    s.add_argument("--fallback",help="Default fallback voice for all remaining missing events")
    s.add_argument("--fallback-category",action="append",default=[],metavar="CATEGORY=VOICE",help="Fill only one semantic category; repeatable")

def _creator_parser(sub):
    c=sub.add_parser("creator",help="Create and build semantic vvh.voicepack.v1 packs")
    cs=c.add_subparsers(dest="creator_cmd",required=True)
    s=cs.add_parser("new");s.add_argument("path",nargs="?");s.add_argument("--id",required=True,dest="pack_id");s.add_argument("--name",required=True);s.add_argument("--author",required=True);s.add_argument("--language",required=True);s.add_argument("--adult",action="store_true");s.add_argument("--license",default="UNLICENSED",dest="license_name");s.add_argument("--source-url");s.add_argument("--description")
    cs.add_parser("list")
    s=cs.add_parser("validate");s.add_argument("path")
    s=cs.add_parser("assign");s.add_argument("path");s.add_argument("semantic");s.add_argument("audio_file")
    s=cs.add_parser("remove");s.add_argument("path");s.add_argument("semantic")
    s=cs.add_parser("coverage");s.add_argument("path");s.add_argument("--model",default="dreame.vacuum.r2209")
    s=cs.add_parser("build");s.add_argument("path");s.add_argument("--model",default="dreame.vacuum.r2209");s.add_argument("--output")
    s=cs.add_parser("events");s.add_argument("--model");s.add_argument("--category")

def _creator_main(a):
    if a.creator_cmd=="new":
        _dump(new_workspace(a.path,pack_id=a.pack_id,name=a.name,author=a.author,language=a.language,adult=a.adult,license_name=a.license_name,source_url=a.source_url,description=a.description))
    elif a.creator_cmd=="list":_dump(list_workspaces())
    elif a.creator_cmd=="validate":_dump(validate_workspace(a.path))
    elif a.creator_cmd=="assign":_dump(assign_audio(a.path,a.semantic,a.audio_file))
    elif a.creator_cmd=="remove":_dump(remove_event(a.path,a.semantic))
    elif a.creator_cmd=="coverage":_dump(workspace_model_coverage(a.path,a.model))
    elif a.creator_cmd=="build":_dump(build_workspace(a.path,a.model,a.output))
    elif a.creator_cmd=="events":
        allowed=set(event_profile_for_model(a.model)["known_event_ids"]) if a.model else None
        rows=[]
        for e in events():
            if allowed is not None and int(e["id"]) not in allowed:continue
            if a.category and e.get("category")!=a.category:continue
            rows.append(e)
        _dump(rows)

def _credential_parser(sub):
    c=sub.add_parser("credential",help="Store robot tokens in the OS secret store")
    cs=c.add_subparsers(dest="credential_cmd",required=True)
    s=cs.add_parser("save");s.add_argument("name");s.add_argument("--token")
    s=cs.add_parser("status");s.add_argument("name")
    s=cs.add_parser("delete");s.add_argument("name")

def _credential_main(a):
    if a.credential_cmd=="save":
        token=a.token or getpass.getpass("TOKEN (32 hex, hidden): ").strip()
        _dump(credentials.save(a.name,token))
    elif a.credential_cmd=="status":
        _dump(credentials.status(a.name))
    elif a.credential_cmd=="delete":
        _dump(credentials.delete(a.name))

def main():
    p=argparse.ArgumentParser(prog="vvh",description=f"Vacuum Voice Hub {__version__}")
    p.add_argument("--version",action="version",version=__version__)
    sub=p.add_subparsers(dest="cmd",required=True)

    s=sub.add_parser("list");s.add_argument("--language");s.add_argument("--adult",action="store_true")
    sub.add_parser("stats")
    sub.add_parser("models")
    s=sub.add_parser("model-info");s.add_argument("model_id")
    s=sub.add_parser("info");s.add_argument("voice_id")
    s=sub.add_parser("coverage");_add_build_args(s)
    s=sub.add_parser("build");_add_build_args(s)
    s=sub.add_parser("install");_add_build_args(s);s.add_argument("--ip",required=True);_add_auth_args(s);s.add_argument("--allow-experimental-transport",action="store_true")
    s=sub.add_parser("web");s.add_argument("--port",type=int,default=8787)
    sub.add_parser("desktop")
    sub.add_parser("doctor")
    s=sub.add_parser("detect");s.add_argument("--ip",required=True);_add_auth_args(s)
    s=sub.add_parser("import-pack");s.add_argument("path");s.add_argument("--model",default="dreame.vacuum.r2209");s.add_argument("--format",default="auto",choices=["auto","dreame-canonical-ogg","robovoice-r2567r-mp3","ijai-named-mp3","roborock-named"]);s.add_argument("--output")
    sub.add_parser("research")
    s=sub.add_parser("preview");s.add_argument("voice_id");s.add_argument("--model",default="dreame.vacuum.r2209");s.add_argument("--play",action="store_true")
    s=sub.add_parser("stock");s.add_argument("--model",default="dreame.vacuum.r2209");s.add_argument("--manifest-url")
    s=sub.add_parser("restore-stock");s.add_argument("stock_id");s.add_argument("--model",default="dreame.vacuum.r2209");s.add_argument("--ip",required=True);_add_auth_args(s);s.add_argument("--manifest-url");s.add_argument("--allow-experimental-transport",action="store_true")
    s=sub.add_parser("history");s.add_argument("--limit",type=int,default=50)
    s=sub.add_parser("report");s.add_argument("--ip",required=True);_add_auth_args(s);s.add_argument("--model");s.add_argument("--output")
    s=sub.add_parser("validate-report");s.add_argument("path")
    release=sub.add_parser("release",help="Build or verify reproducible release bundles")
    rs=release.add_subparsers(dest="release_cmd",required=True)
    s=rs.add_parser("build");s.add_argument("--output",default="release");s.add_argument("--source-date-epoch",type=int)
    s=rs.add_parser("verify");s.add_argument("path",nargs="?",default="release")
    site=sub.add_parser("site",help="Build or verify the static public catalog")
    ss=site.add_subparsers(dest="site_cmd",required=True)
    s=ss.add_parser("build");s.add_argument("--output",default="public")
    s=ss.add_parser("verify");s.add_argument("path",nargs="?",default="public")
    _creator_parser(sub)
    _credential_parser(sub)

    a=p.parse_args()
    if a.cmd=="creator":return _creator_main(a)
    if a.cmd=="credential":return _credential_main(a)
    if a.cmd=="release":
        return _dump(build_release(a.output,a.source_date_epoch) if a.release_cmd=="build" else verify_release(a.path))
    if a.cmd=="site":
        return _dump(build_site(a.output) if a.site_cmd=="build" else verify_site(a.path))

    if a.cmd=="list":
        for v in voices():
            if a.language and v["language"]!=a.language:continue
            if a.adult and not v.get("adult"):continue
            flag=" 🔞" if v.get("adult") else ""
            print(f"{v['id']:<30} {v['language']:<3} {v.get('source_verification','unknown'):<22} {v['title']}{flag}")
    elif a.cmd=="stats":
        vv=voices();mm=models()
        _dump({
            "version":__version__,"voices":len(vv),"adult":sum(bool(v.get("adult")) for v in vv),
            "languages":sorted(set(v["language"] for v in vv)),"models":len(mm),
            "hardware_verified_models":sum(bool(m.get("device_tested")) for m in mm),
            "install_default_models":sum(bool(m.get("transport",{}).get("allow_default")) for m in mm),
            "semantic_events":len(events()),"semantic_categories":categories(),
            "creator_schema":"vvh.voicepack.v1","compat_report_schema":"vvh.compat-report.v1","public_catalog_schema":"vvh.public-catalog.v1","release_manifest_schema":"vvh.release-manifest.v1","update_feed_schema":"vvh.update-feed.v1",
            "research_backlog":len(backlog()),
        })
    elif a.cmd=="models":
        for m in models():
            t=m.get("transport",{})
            print(f"{m['id']:<30} {m['name']:<24} profile={m.get('event_profile','-'):<34} transport={t.get('verification','-')}")
    elif a.cmd=="model-info":_dump(model_by_id(a.model_id))
    elif a.cmd=="info":_dump(voice_by_id(a.voice_id))
    elif a.cmd in {"coverage","build","install"}:
        fbc=_parse_category_fallbacks(a.fallback_category)
        if a.cmd=="coverage":
            b=build_voice(a.voice_id,a.model,fallback_voice_id=a.fallback,fallback_categories=fbc)
            _dump({"voice_id":a.voice_id,"model":b["model"],"compatibility":b["compatibility"],"original_compatibility":b["original_compatibility"],"fallbacks":b.get("fallbacks")})
        elif a.cmd=="build":_dump(build_voice(a.voice_id,a.model,fallback_voice_id=a.fallback,fallback_categories=fbc))
        else:_dump(install_voice(a.voice_id,a.model,a.ip,_resolve_token(a),fallback_voice_id=a.fallback,fallback_categories=fbc,allow_experimental_transport=a.allow_experimental_transport))
    elif a.cmd=="web":serve(a.port)
    elif a.cmd=="desktop":
        from .desktop import main as desktop_main
        desktop_main()
    elif a.cmd=="research":
        for x in backlog():print(f"{x['status']:<38} {x['title']} — {x.get('source_page','')}")
    elif a.cmd=="preview":
        f=preview_file(a.voice_id,a.model);print(f)
        if a.play:
            import subprocess,sys
            player="afplay" if sys.platform=="darwin" else "ffplay"
            subprocess.run([player,str(f)])
    elif a.cmd=="stock":
        r=list_stock(a.model,a.manifest_url);print("manifest:",r["manifest"]);[print(f"{x['id']:<18} {x['size']:>9}  {x['url']}") for x in r["items"]]
    elif a.cmd=="restore-stock":
        r=list_stock(a.model,a.manifest_url);item=next((x for x in r["items"] if x["id"]==a.stock_id),None)
        if not item:raise SystemExit(f"stock id not found: {a.stock_id}")
        _dump(install_stock(a.model,a.ip,_resolve_token(a),item,allow_experimental_transport=a.allow_experimental_transport))
    elif a.cmd=="detect":_dump(miot.info(a.ip,_resolve_token(a)))
    elif a.cmd=="import-pack":_dump(convert_local(a.path,a.model,a.format,a.output))
    elif a.cmd=="history":_dump(load_history(a.limit))
    elif a.cmd=="report":
        _dump(write_report(build_report(a.ip,_resolve_token(a),a.model),a.output))
    elif a.cmd=="validate-report":
        from pathlib import Path
        data=json.loads(Path(a.path).read_text(encoding="utf-8"))
        _dump(validate_report(data))
    elif a.cmd=="doctor":
        import shutil,sys
        print("python:",sys.version.split()[0])
        print("ffmpeg:",shutil.which("ffmpeg") or "bundled via imageio-ffmpeg after install")
        print("ccrypt:",shutil.which("ccrypt") or "optional; required only for legacy Roborock .pkg")
        print("voices:",len(voices()));print("models:",len(models()));print("events:",len(events()))
        print("creator: vvh.voicepack.v1");print("reports: vvh.compat-report.v1");print("public catalog: vvh.public-catalog.v1");print("release manifest: vvh.release-manifest.v1");print("update feed: vvh.update-feed.v1");print("OK")
