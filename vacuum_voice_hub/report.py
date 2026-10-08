import hashlib,json,platform,sys,uuid
from datetime import datetime,timezone
from pathlib import Path
from . import __version__,miot
from .catalog import model_by_id,event_profile_for_model
from .history import latest_for_model,sanitize,TOKEN_RE,IP_RE
from .paths import reports_dir

SCHEMA="vvh.compat-report.v1"
FORBIDDEN_KEYS={"token","ip","mac","url","local_ip","remote_ip","host"}

def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def _transport_public(transport):
    keep=("kind","verification","allow_default","audio_service_siid","set_voice_piid","voice_id_piid","state_piid")
    return {k:transport.get(k) for k in keep if k in transport}

def build_report(ip,token,model_id=None):
    info=miot.info(ip,token)
    actual=info.get("model")
    model=model_by_id(model_id or actual)
    if actual not in model.get("aliases",[]):
        raise ValueError(f"model mismatch: robot={actual} expected one of {model.get('aliases',[])}")
    profile=event_profile_for_model(model["id"])
    transport=model.get("transport",{})
    live=None
    if transport.get("kind")=="miot-local-property":
        try:
            live=miot.voice_status(ip,token,transport)
        except Exception as e:
            live={"error_type":type(e).__name__}
    last=latest_for_model(model["id"])
    candidate=bool(
        last
        and last.get("ok") is True
        and last.get("robot_download_confirmed") is True
        and (last.get("status") or {}).get("state")=="success"
        and (last.get("status") or {}).get("progress")==100
        and live
        and live.get("state")=="success"
        and live.get("progress")==100
    )
    report={
        "schema":SCHEMA,
        "report_id":uuid.uuid4().hex,
        "generated_at":_now(),
        "vvh_version":__version__,
        "platform":{
            "system":platform.system(),
            "release":platform.release(),
            "machine":platform.machine(),
            "python":platform.python_version(),
        },
        "device":{
            "model":actual,
            "firmware":info.get("firmware"),
            "hardware":info.get("hardware"),
        },
        "profile":{
            "id":profile["id"],
            "profile_kind":profile.get("profile_kind"),
            "known_event_count":len(profile.get("known_event_ids",[])),
            "vvh_hardware_verified":bool(profile.get("hardware_verified")),
        },
        "transport":_transport_public(transport),
        "live_voice_status":live,
        "last_install":last,
        "hardware_evidence_candidate":candidate,
        "privacy":{
            "contains_token":False,
            "contains_ip":False,
            "contains_mac":False,
            "note":"Local token, IP address and MAC address are intentionally omitted.",
        },
    }
    return sanitize(report)

def validate_report(report):
    errors=[]
    if report.get("schema")!=SCHEMA:
        errors.append("invalid schema")
    raw=json.dumps(report,ensure_ascii=False)
    if TOKEN_RE.search(raw):
        errors.append("32-hex secret-like value found")
    if IP_RE.search(raw):
        errors.append("IPv4 address found")
    def walk(v,path=""):
        if isinstance(v,dict):
            for k,x in v.items():
                if str(k).lower() in FORBIDDEN_KEYS:
                    errors.append(f"forbidden key: {path}{k}")
                walk(x,path+str(k)+".")
        elif isinstance(v,list):
            for i,x in enumerate(v):walk(x,path+str(i)+".")
    walk(report)
    return {"ok":not errors,"errors":sorted(set(errors))}

def write_report(report,output=None):
    valid=validate_report(report)
    if not valid["ok"]:
        raise ValueError("unsafe compatibility report: "+"; ".join(valid["errors"]))
    out=Path(output).expanduser().resolve() if output else reports_dir()/f"compat-report-{report['report_id']}.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    digest=hashlib.sha256(out.read_bytes()).hexdigest()
    return {"path":str(out),"sha256":digest,"report":report}
