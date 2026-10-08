import json
from miio import Device

def device(ip,token):
    return Device(ip=ip,token=token,timeout=8)

def info(ip,token):
    i=device(ip,token).info()
    return {
        "model":getattr(i,"model",None),
        "firmware":getattr(i,"firmware_version",None),
        "hardware":getattr(i,"hardware_version",None),
        "mac":getattr(i,"mac_address",None),
    }

def _transport_fields(transport):
    return {
        "siid":int(transport.get("audio_service_siid",7)),
        "set_piid":int(transport.get("set_voice_piid",4)),
        "id_piid":int(transport.get("voice_id_piid",2)),
        "state_piid":int(transport.get("state_piid",3)),
    }

def set_voice(ip,token,voice_value,transport):
    kind=transport.get("kind")
    d=device(ip,token)
    if kind=="miot-local-property":
        f=_transport_fields(transport)
        return d.send(
            "set_properties",
            [{"did":"voice-set","siid":f["siid"],"piid":f["set_piid"],"value":voice_value}],
        )
    if kind=="roborock-miio-sound":
        payload={"url":voice_value["url"],"md5":voice_value["md5"],"sid":int(voice_value["sid"])}
        return d.send("dnld_install_sound",payload)
    if kind=="miot-action-url-md5":
        command=transport.get("command")
        if not command:
            raise RuntimeError("MIoT action transport has no command")
        payload={
            "siid":int(transport.get("siid",14)),
            "aiid":int(transport.get("aiid",1)),
            "in":[
                {"piid":int(transport.get("language_piid",1)),"value":transport.get("language_code",voice_value.get("language","ru_RU"))},
                {"piid":int(transport.get("url_piid",5)),"value":voice_value["url"]},
                {"piid":int(transport.get("md5_piid",6)),"value":voice_value["md5"]},
            ],
        }
        return d.send(command,payload)
    raise RuntimeError(f"Local voice installation transport is unsupported: {kind}")

def _decode_state(raw):
    s=raw
    for _ in range(4):
        if not isinstance(s,str):break
        try:s=json.loads(s)
        except Exception:break
    return s

def voice_status(ip,token,transport):
    kind=transport.get("kind")
    d=device(ip,token)
    if kind=="roborock-miio-sound":
        raw=d.send("get_sound_progress")
        value=raw[0] if isinstance(raw,list) and raw else raw
        state=progress=voice_id=None
        if isinstance(value,dict):
            progress=value.get("progress",value.get("pct",value.get("percent")))
            state=value.get("state",value.get("status"))
            voice_id=value.get("sid",value.get("id"))
        elif isinstance(value,(int,float)):
            progress=int(value)
        try:
            progress=int(progress) if progress is not None else None
        except Exception:
            pass
        if progress is not None and isinstance(progress,int):
            if progress>=100:state="success"
            elif not state:state="downloading"
        if isinstance(state,(int,float)):
            state="success" if progress==100 else "downloading"
        return {"voice_id":voice_id,"state":state,"progress":progress,"raw_state":value if state is None else None}
    if kind=="miot-action-url-md5":
        return {"voice_id":None,"state":None,"progress":None,"raw_state":"transport-has-no-local-status"}
    if kind!="miot-local-property":
        raise RuntimeError(f"Voice status unsupported for transport: {kind}")
    f=_transport_fields(transport)
    result=d.send(
        "get_properties",
        [
            {"did":"voice-packet-id","siid":f["siid"],"piid":f["id_piid"]},
            {"did":"voice-change-state","siid":f["siid"],"piid":f["state_piid"]},
        ],
    )
    voice_id=state=progress=None
    raw_state=None
    for x in result or []:
        if not isinstance(x,dict):continue
        if x.get("piid")==f["id_piid"]:voice_id=x.get("value")
        if x.get("piid")==f["state_piid"]:
            raw_state=x.get("value")
            s=_decode_state(raw_state)
            if isinstance(s,dict):
                state=s.get("state");progress=s.get("progress")
    return {"voice_id":voice_id,"state":state,"progress":progress,"raw_state":raw_state if state is None else None}
