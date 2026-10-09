import json,secrets,mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from importlib.resources import files
from urllib.parse import urlparse,parse_qs
from .catalog import voices,models,backlog,categories,model_by_id,events,event_profile_for_model
from .build import build_voice
from .install import install_voice
from .preview import preview_file
from .stock import list_stock,install_stock
from .history import load_history
from .report import build_report,write_report
from .creator import (
    new_workspace,workspace_by_id,list_workspaces,workspace_snapshot,
    assign_audio_bytes,remove_event,build_workspace,update_manifest,load_workspace
)

HTML=(files("vacuum_voice_hub")/"web"/"index.html").read_text(encoding="utf-8")
CREATOR_HTML=(files("vacuum_voice_hub")/"web"/"creator.html").read_text(encoding="utf-8")
CREATOR_SESSION=secrets.token_urlsafe(32)

def _stats():
    vv=voices();mm=models()
    return {
        "voices":len(vv),
        "adult":sum(bool(v.get("adult")) for v in vv),
        "languages":sorted(set(v["language"] for v in vv)),
        "models":len(mm),
        "hardware_verified_models":sum(bool(m.get("device_tested")) for m in mm),
        "backlog":len(backlog()),
        "categories":categories(),
        "target_combinations":len(vv)*len(mm),
        "adapters":sorted({m.get("adapter") for m in mm}),
        "creator_schema":"vvh.voicepack.v1",
        "script_pack_schema":"vvh.script-pack.v1",
        "script_template_locales":18,
    }

def _fallback_categories_from_query(q):
    out={}
    for category in categories():
        value=q.get(f"fallback_{category}",[None])[0]
        if value:out[category]=value
    return out

def _creator_events(model_id=None,category=None):
    allowed=None
    if model_id:
        allowed=set(event_profile_for_model(model_id)["known_event_ids"])
    grouped={}
    for e in events():
        if allowed is not None and int(e["id"]) not in allowed:continue
        if category and e.get("category")!=category:continue
        semantic=e["semantic"]
        g=grouped.setdefault(semantic,{
            "semantic":semantic,
            "category":e.get("category","other"),
            "description":e.get("description"),
            "ids":[],
        })
        g["ids"].append(int(e["id"]))
        if not g.get("description") and e.get("description"):g["description"]=e["description"]
    for g in grouped.values():g["ids"].sort()
    return sorted(grouped.values(),key=lambda x:(x["category"],x["semantic"]))

class H(BaseHTTPRequestHandler):
    def _json(self,obj,status=200):
        b=json.dumps(obj,ensure_ascii=False,default=str).encode()
        self.send_response(status);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)

    def _html(self,text):
        b=text.encode();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)

    def _read_json(self,max_bytes=2_000_000):
        n=int(self.headers.get("Content-Length","0"))
        if n<0 or n>max_bytes:raise ValueError("request too large")
        return json.loads(self.rfile.read(n) or b"{}")

    def _creator_auth(self):
        if self.headers.get("X-VVH-Session")!=CREATOR_SESSION:
            raise PermissionError("invalid Creator Studio session")

    def do_GET(self):
        parsed=urlparse(self.path);q=parse_qs(parsed.query)
        if parsed.path=="/":return self._html(HTML)
        if parsed.path=="/creator":return self._html(CREATOR_HTML)
        if parsed.path=="/api/session":return self._json({"creator_session":CREATOR_SESSION})
        if parsed.path=="/api/script-locales":
            from .script_packs import list_locales
            return self._json({"ok":True,"status":"text-only-not-audio-pack","locales":list_locales()})
        if parsed.path=="/api/script":
            from .script_packs import script_for_model
            try:
                language=q.get("language",[None])[0]
                mid=q.get("model_id",["dreame.vacuum.r2209"])[0]
                return self._json({"ok":True,"script":script_for_model(language,mid)})
            except (ValueError,KeyError) as e:
                return self._json({"ok":False,"error":str(e)},400)
        if parsed.path=="/api/catalog":
            return self._json({"voices":voices(),"models":models(),"backlog":backlog(),"stats":_stats()})
        if parsed.path=="/api/model":
            try:return self._json({"ok":True,"model":model_by_id(q["model_id"][0])})
            except Exception as e:return self._json({"ok":False,"error":str(e)},400)
        if parsed.path=="/api/preview":
            try:
                vid=q["voice_id"][0];mid=q.get("model_id",["dreame.vacuum.r2209"])[0]
                f=preview_file(vid,mid);b=f.read_bytes();self.send_response(200);self.send_header("Content-Type","audio/ogg");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
            except Exception as e:self._json({"ok":False,"error":str(e)},400)
            return
        if parsed.path=="/api/compatibility":
            try:
                vid=q["voice_id"][0];mid=q.get("model_id",["dreame.vacuum.r2209"])[0];fallback=q.get("fallback",[None])[0] or None
                b=build_voice(vid,mid,fallback_voice_id=fallback,fallback_categories=_fallback_categories_from_query(q),package_output=False)
                return self._json({"ok":True,"voice_id":vid,"model_id":b["model"],"compatibility":b["compatibility"],"original_compatibility":b["original_compatibility"],"fallbacks":b.get("fallbacks",[])})
            except Exception as e:return self._json({"ok":False,"error":str(e)},400)
        if parsed.path=="/api/stock":
            try:
                mid=q.get("model_id",["dreame.vacuum.r2209"])[0];return self._json(list_stock(mid))
            except Exception as e:return self._json({"ok":False,"error":str(e)},400)
        if parsed.path=="/api/history":
            try:
                limit=min(200,max(1,int(q.get("limit",["50"])[0])))
                return self._json({"ok":True,"history":load_history(limit)})
            except Exception as e:return self._json({"ok":False,"error":str(e)},400)

        if parsed.path=="/api/creator/preflight":
            from .creator_batch import preflight_workspace
            try:
                wid=q["id"][0]
                mid=q.get("model_id",["dreame.vacuum.r2209"])[0]
                check=q.get("check_audio",["false"])[0].lower()=="true"
                return self._json({"ok":True,"report":preflight_workspace(workspace_by_id(wid),mid,check_audio=check)})
            except (KeyError,ValueError,FileNotFoundError,OSError) as exc:
                return self._json({"ok":False,"error":str(exc)},400)
        if parsed.path=="/api/creator/qa":
            from .audio_qa import inspect_workspace
            try:
                wid=q["id"][0]
                mid=q.get("model_id",[None])[0]
                return self._json({"ok":True,"report":inspect_workspace(workspace_by_id(wid),mid)})
            except (KeyError,ValueError,FileNotFoundError,OSError) as e:
                return self._json({"ok":False,"error":str(e)},400)
        if parsed.path=="/api/creator/workspaces":
            return self._json({"ok":True,"workspaces":list_workspaces()})
        if parsed.path=="/api/creator/events":
            try:
                return self._json({"ok":True,"events":_creator_events(q.get("model_id",[None])[0],q.get("category",[None])[0])})
            except Exception as e:return self._json({"ok":False,"error":str(e)},400)
        if parsed.path=="/api/creator/workspace":
            try:
                wid=q["id"][0];model_id=q.get("model_id",[None])[0]
                return self._json({"ok":True,**workspace_snapshot(workspace_by_id(wid),model_id)})
            except Exception as e:return self._json({"ok":False,"error":str(e)},400)
        if parsed.path=="/api/creator/audio":
            try:
                if q.get("session",[None])[0]!=CREATOR_SESSION:
                    raise PermissionError("invalid Creator Studio session")
                wid=q["id"][0];semantic=q["semantic"][0]
                root,manifest=load_workspace(workspace_by_id(wid))
                rel=manifest.get("events",{}).get(semantic)
                if not rel:raise FileNotFoundError("semantic has no assigned audio")
                p=(root/rel).resolve();p.relative_to(root)
                b=p.read_bytes();ctype=mimetypes.guess_type(p.name)[0] or "application/octet-stream"
                self.send_response(200);self.send_header("Content-Type",ctype);self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
            except PermissionError as e:self._json({"ok":False,"error":str(e)},403)
            except Exception as e:self._json({"ok":False,"error":str(e)},404)
            return
        self.send_error(404)

    def do_POST(self):
        parsed=urlparse(self.path);q=parse_qs(parsed.query)
        try:
            if parsed.path=="/api/creator/audio":
                self._creator_auth()
                n=int(self.headers.get("Content-Length","0"))
                if n<=0 or n>25*1024*1024:raise ValueError("audio upload must be 1 byte..25 MiB")
                data=self.rfile.read(n)
                wid=q["id"][0];semantic=q["semantic"][0];filename=q.get("filename",["upload.wav"])[0]
                return self._json({"ok":True,**assign_audio_bytes(workspace_by_id(wid),semantic,filename,data)})

            d=self._read_json()
            if parsed.path=="/api/install":
                result=install_voice(d["voice_id"],d["model_id"],d["ip"],d["token"],fallback_voice_id=d.get("fallback") or None,fallback_categories=d.get("fallback_categories") or {},allow_experimental_transport=bool(d.get("allow_experimental_transport")))
            elif parsed.path=="/api/report":
                result=write_report(build_report(d["ip"],d["token"],d.get("model_id")))
            elif parsed.path=="/api/restore-stock":
                stock=list_stock(d["model_id"]);item=next((x for x in stock["items"] if x["id"]==d["stock_id"]),None)
                if not item:raise ValueError("stock id not found")
                result=install_stock(d["model_id"],d["ip"],d["token"],item,allow_experimental_transport=bool(d.get("allow_experimental_transport")))
            elif parsed.path.startswith("/api/creator/"):
                self._creator_auth()
                if parsed.path=="/api/creator/new":
                    result=new_workspace(None,pack_id=d["id"],name=d["name"],author=d["author"],language=d["language"],adult=bool(d.get("adult")),license_name=d.get("license") or "UNLICENSED",source_url=d.get("source_url"),description=d.get("description"))
                elif parsed.path=="/api/creator/manifest":
                    result=update_manifest(workspace_by_id(d["id"]),d.get("updates") or {})
                elif parsed.path=="/api/creator/remove":
                    result=remove_event(workspace_by_id(d["id"]),d["semantic"])
                elif parsed.path=="/api/creator/build":
                    result=build_workspace(workspace_by_id(d["id"]),d["model_id"],d.get("output"))
                elif parsed.path=="/api/creator/batch":
                    from .creator_batch import batch_build_workspace
                    from .paths import data_dir
                    import secrets
                    wid=d["id"]
                    target_models=d["models"]
                    output_dir=data_dir()/"creator-batches"/(wid+"__"+secrets.token_hex(8))
                    result=batch_build_workspace(workspace_by_id(wid),target_models,output_dir,
                                                 check_audio=bool(d.get("check_audio",False)))

                else:return self.send_error(404)
            else:return self.send_error(404)
            self._json({"ok":True,**result} if isinstance(result,dict) and "ok" not in result else result)
        except PermissionError as e:self._json({"ok":False,"error":str(e)},403)
        except Exception as e:self._json({"ok":False,"error":str(e)},400)

    def log_message(self,*a):pass

def make_server(port=8787):
    return ThreadingHTTPServer(("127.0.0.1",port),H)

def serve(port=8787):
    server=make_server(port)
    actual_port=server.server_address[1]
    print(f"Vacuum Voice Hub → http://127.0.0.1:{actual_port}")
    print(f"Creator Studio → http://127.0.0.1:{actual_port}/creator")
    print("The UI is bound to localhost only. Ctrl+C to stop.")
    try:
        server.serve_forever()
    finally:
        server.server_close()
