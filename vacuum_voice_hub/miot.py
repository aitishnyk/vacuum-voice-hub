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
    if kind!="miot-local-property":
        raise RuntimeError(f"Local voice installation transport is unsupported: {kind}")
    f=_transport_fields(transport)
    return device(ip,token).send(
        "set_properties",
        [{"did":"voice-set","siid":f["siid"],"piid":f["set_piid"],"value":voice_value}],
    )

def voice_status(ip,token,transport):
    f=_transport_fields(transport)
    result=device(ip,token).send(
        "get_properties",
        [
            {"did":"voice-packet-id","siid":f["siid"],"piid":f["id_piid"]},
            {"did":"voice-change-state","siid":f["siid"],"piid":f["state_piid"]},
        ],
    )
    voice_id=state=progress=None
    raw_state=None
    for x in result or []:
        if not isinstance(x,dict):
            continue
        if x.get("piid")==f["id_piid"]:
            voice_id=x.get("value")
        if x.get("piid")==f["state_piid"]:
            raw_state=x.get("value")
            s=raw_state
            for _ in range(4):
                if not isinstance(s,str):
                    break
                try:
                    s=json.loads(s)
                except Exception:
                    break
            if isinstance(s,dict):
                state=s.get("state")
                progress=s.get("progress")
    return {
        "voice_id":voice_id,
        "state":state,
        "progress":progress,
        "raw_state":raw_state if state is None else None,
    }
