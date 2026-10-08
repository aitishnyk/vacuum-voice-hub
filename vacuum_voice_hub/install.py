import getpass,http.server,socket,socketserver,threading,time,re
from pathlib import Path
from .build import build_voice
from .catalog import model_by_id
from .models.registry import get as get_model
from . import miot

TOKEN_RE=re.compile(r"^[0-9a-fA-F]{32}$")

def local_ip_for(remote_ip):
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        s.connect((remote_ip,9))
        return s.getsockname()[0]
    finally:
        s.close()

class DownloadTracker:
    def __init__(self,robot_ip,target_name):
        self.robot_ip=robot_ip
        self.target_name=target_name
        self.robot_gets=0
        self.event=threading.Event()

def handler_factory(directory,tracker):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,fmt,*args):
            pass
        def do_GET(self):
            super().do_GET()
            if self.client_address[0]==tracker.robot_ip and self.path.split("?")[0].endswith("/"+tracker.target_name):
                tracker.robot_gets+=1
                tracker.event.set()
    return lambda *a,**kw: Handler(*a,directory=str(directory),**kw)

def _validate_transport(model,allow_experimental_transport):
    transport=model.get("transport",{})
    if transport.get("kind")!="miot-local-property":
        raise RuntimeError(
            f"{model['name']} is build/coverage-only in VVH: no verified local set-voice transport. "
            "Use a rooted/Valetudo workflow or contribute device evidence."
        )
    if not transport.get("allow_default",False) and not allow_experimental_transport:
        raise RuntimeError(
            f"{model['name']} transport is {transport.get('verification','unverified')}. "
            "Refusing installation without --allow-experimental-transport."
        )
    return transport

def install_voice(
    voice_id,model_id,ip,token=None,timeout=180,
    fallback_voice_id=None,fallback_categories=None,
    allow_experimental_transport=False,
):
    token=token or getpass.getpass("TOKEN (32 hex, hidden): ").strip()
    if not TOKEN_RE.fullmatch(token):
        raise ValueError("token must be exactly 32 hexadecimal characters")
    model=model_by_id(model_id)
    transport=_validate_transport(model,allow_experimental_transport)
    di=miot.info(ip,token)
    if di.get("model") not in model.get("aliases",[]):
        raise ValueError(f"model mismatch: robot={di.get('model')} expected one of {model.get('aliases',[])}")
    built=build_voice(
        voice_id,model["id"],
        fallback_voice_id=fallback_voice_id,
        fallback_categories=fallback_categories,
    )
    path=Path(built["path"])
    host=local_ip_for(ip)
    tracker=DownloadTracker(ip,path.name)
    handler=handler_factory(path.parent,tracker)
    class S(socketserver.ThreadingMixIn,http.server.HTTPServer):
        daemon_threads=True
    srv=S(("0.0.0.0",0),handler)
    port=srv.server_address[1]
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    try:
        url=f"http://{host}:{port}/{path.name}"
        pack_id=voice_id.upper().replace("-","")[:12]
        value=get_model(model["id"]).make_voice_value(pack_id,url,built["md5"],built["size"])
        result=miot.set_voice(ip,token,value,transport)
        codes=[x.get("code") for x in (result or []) if isinstance(x,dict)]
        if 0 not in codes:
            raise RuntimeError(f"robot rejected set-voice: {result}")
        deadline=time.time()+timeout
        last={}
        while time.time()<deadline:
            time.sleep(3)
            last=miot.voice_status(ip,token,transport)
            if last.get("state")=="success" and last.get("progress")==100:
                return {
                    "ok":True,
                    "device":{
                        "model":di.get("model"),
                        "firmware":di.get("firmware"),
                        "hardware":di.get("hardware"),
                    },
                    "transport_verification":transport.get("verification"),
                    "robot_download_confirmed":tracker.event.is_set(),
                    "robot_download_requests":tracker.robot_gets,
                    "status":last,
                    "compatibility":built["compatibility"],
                    "fallbacks":built.get("fallbacks",[]),
                    "package":{"md5":built["md5"],"size":built["size"],"events":built["events"]},
                }
            if last.get("state") in {"failed","fail","error"}:
                raise RuntimeError(f"installation failed: {last}")
        raise TimeoutError(
            f"installation timeout; robot_download_confirmed={tracker.event.is_set()} last={last}"
        )
    finally:
        srv.shutdown()
        srv.server_close()
