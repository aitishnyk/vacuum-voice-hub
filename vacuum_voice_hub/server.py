import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from importlib.resources import files
from urllib.parse import urlparse,parse_qs
from .catalog import voices,models,backlog,categories,model_by_id
from .build import build_voice
from .install import install_voice
from .preview import preview_file
from .stock import list_stock,install_stock

HTML=(files("vacuum_voice_hub")/"web"/"index.html").read_text(encoding="utf-8")

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
    }

def _fallback_categories_from_query(q):
    out={}
    for category in categories():
        value=q.get(f"fallback_{category}",[None])[0]
        if value:out[category]=value
    return out

class H(BaseHTTPRequestHandler):
    def _json(self,obj,status=200):
        b=json.dumps(obj,ensure_ascii=False,default=str).encode()
        self.send_response(status);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        parsed=urlparse(self.path)
        if parsed.path=="/":
            b=HTML.encode();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b);return
        if parsed.path=="/api/catalog":
            return self._json({"voices":voices(),"models":models(),"backlog":backlog(),"stats":_stats()})
        if parsed.path=="/api/model":
            try:
                q=parse_qs(parsed.query);return self._json({"ok":True,"model":model_by_id(q["model_id"][0])})
            except Exception as e:return self._json({"ok":False,"error":str(e)},400)
        if parsed.path=="/api/preview":
            try:
                q=parse_qs(parsed.query);vid=q["voice_id"][0];mid=q.get("model_id",["dreame.vacuum.r2209"])[0]
                f=preview_file(vid,mid);b=f.read_bytes();self.send_response(200);self.send_header("Content-Type","audio/ogg");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
            except Exception as e:self._json({"ok":False,"error":str(e)},400)
            return
        if parsed.path=="/api/compatibility":
            try:
                q=parse_qs(parsed.query);vid=q["voice_id"][0];mid=q.get("model_id",["dreame.vacuum.r2209"])[0];fallback=q.get("fallback",[None])[0] or None
                b=build_voice(vid,mid,fallback_voice_id=fallback,fallback_categories=_fallback_categories_from_query(q))
                return self._json({"ok":True,"voice_id":vid,"model_id":b["model"],"compatibility":b["compatibility"],"original_compatibility":b["original_compatibility"],"fallbacks":b.get("fallbacks",[])})
            except Exception as e:return self._json({"ok":False,"error":str(e)},400)
        if parsed.path=="/api/stock":
            try:
                q=parse_qs(parsed.query);mid=q.get("model_id",["dreame.vacuum.r2209"])[0];return self._json(list_stock(mid))
            except Exception as e:return self._json({"ok":False,"error":str(e)},400)
        self.send_error(404)
    def do_POST(self):
        try:
            n=int(self.headers.get("Content-Length","0"))
            if n>2_000_000:raise ValueError("request too large")
            d=json.loads(self.rfile.read(n) or b"{}")
            if self.path=="/api/install":
                result=install_voice(
                    d["voice_id"],d["model_id"],d["ip"],d["token"],
                    fallback_voice_id=d.get("fallback") or None,
                    fallback_categories=d.get("fallback_categories") or {},
                    allow_experimental_transport=bool(d.get("allow_experimental_transport")),
                )
            elif self.path=="/api/restore-stock":
                stock=list_stock(d["model_id"]);item=next((x for x in stock["items"] if x["id"]==d["stock_id"]),None)
                if not item:raise ValueError("stock id not found")
                result=install_stock(d["model_id"],d["ip"],d["token"],item,allow_experimental_transport=bool(d.get("allow_experimental_transport")))
            else:return self.send_error(404)
            self._json(result)
        except Exception as e:self._json({"ok":False,"error":str(e)},400)
    def log_message(self,*a):pass

def serve(port=8787):
    print(f"Vacuum Voice Hub → http://127.0.0.1:{port}")
    print("The UI is bound to localhost only. Ctrl+C to stop.")
    ThreadingHTTPServer(("127.0.0.1",port),H).serve_forever()
