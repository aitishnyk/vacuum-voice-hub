import argparse, json, sys
from .catalog import voices,models,voice_by_id,backlog
from .build import build_voice
from .install import install_voice
from .server import serve
from .stock import list_stock, install_stock
from .preview import preview_file
from .local_import import convert_local
from . import miot

def main():
    p=argparse.ArgumentParser(prog="vvh",description="Vacuum Voice Hub")
    sub=p.add_subparsers(dest="cmd",required=True)
    s=sub.add_parser("list"); s.add_argument("--language"); s.add_argument("--adult",action="store_true"); s.add_argument("--all",action="store_true")
    sub.add_parser("models")
    s=sub.add_parser("info"); s.add_argument("voice_id")
    s=sub.add_parser("build"); s.add_argument("voice_id"); s.add_argument("--model",default="dreame.vacuum.r2209")
    s=sub.add_parser("install"); s.add_argument("voice_id"); s.add_argument("--model",default="dreame.vacuum.r2209"); s.add_argument("--ip",required=True); s.add_argument("--token")
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
            flag=" 🔞" if v.get("adult") else ""; print(f"{v['id']:<24} {v['language']:<3} {v['title']}{flag}")
    elif a.cmd=="models":
        for m in models(): print(f"{m['id']:<28} {m['name']}  tested={m.get('device_tested',False)}")
    elif a.cmd=="info": print(json.dumps(voice_by_id(a.voice_id),ensure_ascii=False,indent=2))
    elif a.cmd=="build": print(json.dumps(build_voice(a.voice_id,a.model),ensure_ascii=False,indent=2,default=str))
    elif a.cmd=="install": print(json.dumps(install_voice(a.voice_id,a.model,a.ip,a.token),ensure_ascii=False,indent=2))
    elif a.cmd=="web": serve(a.port)
    elif a.cmd=="research":
        for x in backlog(): print(f"{x['status']:<22} {x['title']} — {x.get('source_page','')}")
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
        print(json.dumps(install_stock(a.model,a.ip,token,item),ensure_ascii=False,indent=2))
    elif a.cmd=="detect":
        import getpass
        token=a.token or getpass.getpass("TOKEN (hidden): ")
        print(json.dumps(miot.info(a.ip,token),ensure_ascii=False,indent=2))
    elif a.cmd=="import-pack":
        print(json.dumps(convert_local(a.path,a.model,a.format,a.output),ensure_ascii=False,indent=2,default=str))
    elif a.cmd=="doctor":
        import shutil,sys
        print("python:",sys.version.split()[0]); print("ffmpeg:",shutil.which("ffmpeg") or "bundled via imageio-ffmpeg after install")
        print("voices:",len(voices())); print("models:",len(models())); print("OK")
