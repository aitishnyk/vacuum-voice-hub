import json
from miio import Device

def device(ip,token): return Device(ip=ip, token=token, timeout=8)

def info(ip,token):
    i=device(ip,token).info()
    return {"model":getattr(i,"model",None),"firmware":getattr(i,"firmware_version",None),"hardware":getattr(i,"hardware_version",None),"mac":getattr(i,"mac_address",None)}

def set_voice(ip,token,voice_value):
    return device(ip,token).send("set_properties",[{"did":"voice-set","siid":7,"piid":4,"value":voice_value}])

def voice_status(ip,token):
    result=device(ip,token).send("get_properties",[
        {"did":"voice-packet-id","siid":7,"piid":2},
        {"did":"voice-change-state","siid":7,"piid":3},
    ])
    voice_id=state=progress=None
    for x in result or []:
        if not isinstance(x,dict): continue
        if x.get("piid")==2: voice_id=x.get("value")
        if x.get("piid")==3:
            s=x.get("value")
            for _ in range(4):
                if not isinstance(s,str): break
                try: s=json.loads(s)
                except Exception: break
            if isinstance(s,dict): state=s.get("state"); progress=s.get("progress")
    return {"voice_id":voice_id,"state":state,"progress":progress}
