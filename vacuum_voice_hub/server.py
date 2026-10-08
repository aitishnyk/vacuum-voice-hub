import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from .catalog import voices,models,backlog
from .install import install_voice
from .preview import preview_file
from .stock import list_stock, install_stock
from urllib.parse import urlparse, parse_qs

HTML=(files("vacuum_voice_hub")/"web"/"index.html").read_text(encoding="utf-8")
class H(BaseHTTPRequestHandler):
    def _json(self,obj,status=200):
        b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        parsed=urlparse(self.path)
        if parsed.path=="/api/preview":
            try:
                q=parse_qs(parsed.query); vid=q["voice_id"][0]; mid=q.get("model_id",["dreame.vacuum.r2209"])[0]
                f=preview_file(vid,mid); b=f.read_bytes(); self.send_response(200); self.send_header("Content-Type","audio/ogg"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
            except Exception as e: self._json({"ok":False,"error":str(e)},400)
            return
        if parsed.path=="/":
            b=HTML.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b); return
        if parsed.path=="/api/catalog": return self._json({"voices":voices(),"models":models(),"backlog":backlog()})
        if parsed.path=="/api/stock":
            try:
                q=parse_qs(parsed.query); mid=q.get("model_id",["dreame.vacuum.r2209"])[0]; return self._json(list_stock(mid))
            except Exception as e: return self._json({"ok":False,"error":str(e)},400)
        self.send_error(404)
    def do_POST(self):
        try:
            n=int(self.headers.get("Content-Length","0")); d=json.loads(self.rfile.read(n) or b"{}")
            if self.path=="/api/install": result=install_voice(d["voice_id"],d["model_id"],d["ip"],d["token"])
            elif self.path=="/api/restore-stock":
                stock=list_stock(d["model_id"]); item=next((x for x in stock["items"] if x["id"]==d["stock_id"]),None)
                if not item: raise ValueError("stock id not found")
                result=install_stock(d["model_id"],d["ip"],d["token"],item)
            else: return self.send_error(404)
            self._json(result)
        except Exception as e: self._json({"ok":False,"error":str(e)},400)
    def log_message(self,*a): pass

def serve(port=8787):
    print(f"Vacuum Voice Hub → http://127.0.0.1:{port}")
    print("The UI is bound to localhost only. Ctrl+C to stop.")
    ThreadingHTTPServer(("127.0.0.1",port),H).serve_forever()
