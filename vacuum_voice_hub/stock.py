import json, urllib.request
from .models.registry import get as get_model

def manifest_url(model_id):
    return f"https://awsde0.fds.api.xiaomi.com/dreame-product/{model_id}/voices/soundpackage.json"

def _walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from _walk(v)
    elif isinstance(x,list):
        for v in x: yield from _walk(v)

def _first(d,keys):
    for k in keys:
        if k in d and d[k] not in (None,""): return d[k]

def list_stock(model_id, url=None):
    url=url or manifest_url(model_id)
    req=urllib.request.Request(url,headers={"User-Agent":"VacuumVoiceHub/0.1"})
    with urllib.request.urlopen(req,timeout=30) as r: data=json.load(r)
    out=[]
    for d in _walk(data):
        u=_first(d,["url","downloadUrl","download_url","voiceUrl","voice_url"])
        md5=_first(d,["md5","hash","md5sum"]); size=_first(d,["size","fileSize","filesize","file_size"])
        if not (isinstance(u,str) and u.startswith("http") and md5 and size): continue
        ident=_first(d,["id","lang","lang_id","language","languageId","name","displayName"]) or f"stock-{len(out)+1}"
        try: size=int(size)
        except Exception: continue
        item={"id":str(ident),"url":u,"md5":str(md5),"size":size}
        if item not in out: out.append(item)
    return {"manifest":url,"items":out,"raw":data}

def install_stock(model_id, ip, token, item):
    from . import miot
    info=miot.info(ip,token)
    if info.get("model")!=model_id: raise ValueError(f"model mismatch: {info.get('model')} != {model_id}")
    value=get_model(model_id).make_voice_value(item["id"],item["url"],item["md5"],int(item["size"]))
    result=miot.set_voice(ip,token,value)
    return {"device":info,"result":result}
