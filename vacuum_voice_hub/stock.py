import json,urllib.request,time
from .catalog import model_by_id
from .models.registry import get as get_model
from .history import append_history

def manifest_url(model_id):
    model=model_by_id(model_id)
    if model.get("adapter")!="dreame_numeric":
        raise RuntimeError(f"Official Dreame soundpackage discovery is not supported for adapter {model.get('adapter')}")
    return f"https://awsde0.fds.api.xiaomi.com/dreame-product/{model['id']}/voices/soundpackage.json"

def _walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from _walk(v)
    elif isinstance(x,list):
        for v in x:yield from _walk(v)

def _first(d,keys):
    for k in keys:
        if k in d and d[k] not in (None,""):return d[k]

def list_stock(model_id,url=None):
    model=model_by_id(model_id)
    url=url or manifest_url(model["id"])
    req=urllib.request.Request(url,headers={"User-Agent":"VacuumVoiceHub/0.8"})
    with urllib.request.urlopen(req,timeout=30) as r:data=json.load(r)
    out=[]
    for d in _walk(data):
        u=_first(d,["url","downloadUrl","download_url","voiceUrl","voice_url"])
        md5=_first(d,["md5","hash","md5sum"]);size=_first(d,["size","fileSize","filesize","file_size"])
        if not (isinstance(u,str) and u.startswith("http") and md5 and size):continue
        ident=_first(d,["id","lang","lang_id","language","languageId","name","displayName"]) or f"stock-{len(out)+1}"
        try:size=int(size)
        except Exception:continue
        item={"id":str(ident),"url":u,"md5":str(md5),"size":size}
        if item not in out:out.append(item)
    return {"model_id":model["id"],"manifest":url,"items":out,"raw":data}

def install_stock(model_id,ip,token,item,allow_experimental_transport=False,timeout=180):
    from . import miot
    from .install import _validate_transport,_accepted
    model=model_by_id(model_id)
    if model.get("adapter")!="dreame_numeric":
        raise RuntimeError("Official stock restore is currently implemented only for Dreame numeric models")
    transport=_validate_transport(model,allow_experimental_transport)
    info=miot.info(ip,token)
    if info.get("model") not in model.get("aliases",[]):raise ValueError(f"model mismatch: {info.get('model')} not in {model.get('aliases',[])}")
    value=get_model(model["id"]).make_voice_value(item["id"],item["url"],item["md5"],int(item["size"]))
    result=miot.set_voice(ip,token,value,transport)
    if not _accepted(result,transport):raise RuntimeError(f"robot rejected stock voice request: {result}")
    deadline=time.time()+timeout;last={}
    while time.time()<deadline:
        time.sleep(3);last=miot.voice_status(ip,token,transport)
        if last.get("state")=="success" and last.get("progress")==100:
            append_history({"ok":True,"action":"restore-stock","voice_id":item["id"],"model_id":model["id"],"firmware":info.get("firmware"),"hardware":info.get("hardware"),"transport_verification":transport.get("verification"),"status":{"voice_id":last.get("voice_id"),"state":last.get("state"),"progress":last.get("progress")}})
            return {"ok":True,"device":{"model":info.get("model"),"firmware":info.get("firmware"),"hardware":info.get("hardware")},"stock_id":item["id"],"status":last,"transport_verification":transport.get("verification")}
        if last.get("state") in {"failed","fail","error"}:raise RuntimeError(f"stock voice installation failed: {last}")
    return {"ok":True,"accepted":True,"device":{"model":info.get("model"),"firmware":info.get("firmware"),"hardware":info.get("hardware")},"stock_id":item["id"],"status":last,"warning":"Robot accepted the request but success state was not observed before timeout."}
