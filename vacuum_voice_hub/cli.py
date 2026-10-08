import argparse, json
from .catalog import voices,models,voice_by_id,backlog
from .build import build_voice
from .install import install_voice
from .server import serve
from .stock import list_stock, install_stock
from .preview import preview_file
from .local_import import convert_local
from . import miot, __version__

def _dump(x): print(json.dumps(x,ensure_ascii=False,indent=2,default=str))

def main():
    p=argparse.ArgumentParser(prog="vvh",description=f"Vacuum Voice Hub {__version__}")
    p.add_argument("--version",action="version",version=__version__)
    sub=p.add_subparsers(dest="cmd",required=True)
    s=sub.add_parser("list"); s.add_argument("--language"); s.add_argument("--adult",action="store_true")
    sub.add_parser("stats")
    sub.add_parser("models")
    s=sub.add_parser("info"); s.add_argument("voice_id")
    s=sub.add_parser("coverage"); s.add_argument("voice_id"); s.add_argument("--model",default="dreame.vacuum.r2209"); s.add_argument("--fallback")
    s=sub.add_parser("build"); s.add_argument("voice_id"); s.add_argument("--model",default="dreame.vacuum.r2209"); s.add_argument("--fallback")
    s=sub.add_parser("install"); s.add_argument("voice_id"); s.add_argument("--model",default="dreame.vacuum.r2209"); s.add_argument("--fallback"); s.add_argument("--ip",required=True); s.add_argument("--token")
    s=sub.add_parser("web"); s.add_argument("--port",type=int,default=8787)
    sub.add_parser("doctor")
    s=sub.add_parser("detect"); s.add_argument("--ip",required=True); s.add_argument("--token")
    s=sub.add_parser("import-pack"); s.add_argument("path"); s.add_argument("--model",default="dreame.vacuum.r2209"); s.add_argument("--format",default="auto",choices=["auto","dreame-canonical-ogg","robovoice-r2567r-mp3","ijai-named-mp3","roborock-named"]); s.add_argument("--output")
    sub.add_parser("research")
    s=sub.add_parser("preview"); s.add_argument("voice_id"); s.add_argument("--model",default="dreame.vacuum.r2209"); s.add_argument("--play",action="store_true")
    s=sub.add_parser("stock"); s.add_argument("--model",default="dreame.vacuum.r2209"); s.add_argument("--manifest-url")
    s=sub.add_parser("restore-stock"); s.add_argument("stock_id"); s.add_argument("--model",default="dreame.vacuum.r2209"); s.add_argument("--ip",required=True); s.add_argument("--token"); s.add_argument("--manifest-url")
    a=p.parse_args()
    if a.cmd=="list":
        for v in voices():
            if a.language and v["language"]!=a.language: continue
            if a.adult and not v.get("adult"): continue
            flag=" 🔞" if v.get("adult") else ""
            verify=v.get("source_verification","unknown")
            print(f"{v['id']:<28} {v['language']:<3} {verify:<20} {v['title']}{flag}")
    elif a.cmd=="stats":
        vv=voices()
        _dump({"version":__version__,"voices":len(vv),"adult":sum(bool(v.get("adult")) for v in vv),"languages":sorted(set(v["language"] for v in vv)),"models":len(models()),"research_backlog":len(backlog())})
    elif a.cmd=="models":
        for m in models(): print(f"{m['id']:<28} {m['name']}  tested={m.get('device_tested',False)} profile={m.get('event_profile','-')}")
    elif a.cmd=="info": _dump(voice_by_id(a.voice_id))
    elif a.cmd=="coverage":
        b=build_voice(a.voice_id,a.model,fallback_voice_id=a.fallback)
        _dump({"voice_id":a.voice_id,"model":a.model,"compatibility":b["compatibility"],"original_compatibility":b["original_compatibility"],"fallback":b.get("fallback")})
    elif a.cmd=="build": _dump(build_voice(a.voice_id,a.model,fallback_voice_id=a.fallback))
    elif a.cmd=="install": _dump(install_voice(a.voice_id,a.model,a.ip,a.token,fallback_voice_id=a.fallback))
    elif a.cmd=="web": serve(a.port)
    elif a.cmd=="research":
        for x in backlog(): print(f"{x['status']:<34} {x['title']} — {x.get('source_page','')}")
    elif a.cmd=="preview":
        f=preview_file(a.voice_id,a.model); print(f)
        if a.play:
            import subprocess,sys
            player="afplay" if sys.platform=="darwin" else "ffplay"
            subprocess.run([player,str(f)])
    elif a.cmd=="stock":
        r=list_stock(a.model,a.manifest_url); print("manifest:",r["manifest"]); [print(f"{x['id']:<18} {x['size']:>9}  {x['url']}") for x in r["items"]]
    elif a.cmd=="restore-stock":
        import getpass
        r=list_stock(a.model,a.manifest_url); item=next((x for x in r["items"] if x["id"]==a.stock_id),None)
        if not item: raise SystemExit(f"stock id not found: {a.stock_id}")
        token=a.token or getpass.getpass("TOKEN (hidden): ")
        _dump(install_stock(a.model,a.ip,token,item))
    elif a.cmd=="detect":
        import getpass
        token=a.token or getpass.getpass("TOKEN (hidden): ")
        _dump(miot.info(a.ip,token))
    elif a.cmd=="import-pack":
        _dump(convert_local(a.path,a.model,a.format,a.output))
    elif a.cmd=="doctor":
        import shutil,sys
        print("python:",sys.version.split()[0])
        print("ffmpeg:",shutil.which("ffmpeg") or "bundled via imageio-ffmpeg after install")
        print("ccrypt:",shutil.which("ccrypt") or "optional; required only for legacy Roborock .pkg")
        print("voices:",len(voices())); print("models:",len(models())); print("OK")
