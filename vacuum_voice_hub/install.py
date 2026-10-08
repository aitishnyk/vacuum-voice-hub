import getpass, http.server, socket, socketserver, threading, time
from pathlib import Path
from .build import build_voice
from .catalog import model_by_id
from .models.registry import get as get_model
from . import miot

def local_ip_for(remote_ip):
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try: s.connect((remote_ip,9)); return s.getsockname()[0]
    finally: s.close()

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,fmt,*args): pass

def install_voice(voice_id, model_id, ip, token=None, timeout=150, fallback_voice_id=None):
    token=token or getpass.getpass("TOKEN (32 hex, hidden): ").strip()
    if len(token)!=32: raise ValueError("token must be 32 characters")
    model=model_by_id(model_id)
    di=miot.info(ip,token)
    if di.get("model") not in model.get("aliases",[]): raise ValueError(f"model mismatch: robot={di.get('model')} expected={model_id}")
    built=build_voice(voice_id,model_id,fallback_voice_id=fallback_voice_id); path=Path(built["path"]); host=local_ip_for(ip)
    handler=lambda *a,**kw: Quiet(*a,directory=str(path.parent),**kw)
    class S(socketserver.ThreadingMixIn,http.server.HTTPServer): daemon_threads=True
    srv=S(("0.0.0.0",0),handler); port=srv.server_address[1]
    th=threading.Thread(target=srv.serve_forever,daemon=True); th.start()
    try:
        url=f"http://{host}:{port}/{path.name}"
        pack_id=voice_id.upper().replace("-","")[:12]
        value=get_model(model_id).make_voice_value(pack_id,url,built["md5"],built["size"])
        result=miot.set_voice(ip,token,value)
        if not any(isinstance(x,dict) and x.get("code")==0 for x in (result or [])): raise RuntimeError(f"robot rejected request: {result}")
        deadline=time.time()+timeout; last={}
        while time.time()<deadline:
            time.sleep(3); last=miot.voice_status(ip,token)
            if last.get("state")=="success" and last.get("progress")==100:
                return {
                    "ok":True,
                    "device":di,
                    "status":last,
                    "compatibility":built["compatibility"],
                    "fallback":built.get("fallback"),
                    "package":{"md5":built["md5"],"size":built["size"],"events":built["events"]},
                }
            if last.get("state") in {"failed","fail","error"}: raise RuntimeError(f"installation failed: {last}")
        raise TimeoutError(f"installation timeout; last={last}")
    finally: srv.shutdown(); srv.server_close()
