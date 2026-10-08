import json,re
from datetime import datetime,timezone
from .paths import history_file

SECRET_KEYS={"token","ip","mac","url","local_ip","remote_ip","host"}
TOKEN_RE=re.compile(r"\b[0-9a-fA-F]{32}\b")
IP_RE=re.compile(r"(?<![0-9])(?:\d{1,3}\.){3}\d{1,3}(?![0-9])")
MAX_ENTRIES=500

def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def sanitize(value):
    if isinstance(value,dict):
        out={}
        for k,v in value.items():
            if str(k).lower() in SECRET_KEYS:
                continue
            out[k]=sanitize(v)
        return out
    if isinstance(value,list):
        return [sanitize(v) for v in value]
    if isinstance(value,str):
        value=TOKEN_RE.sub("[redacted-token]",value)
        value=IP_RE.sub("[redacted-ip]",value)
    return value

def append_history(record):
    p=history_file()
    clean=sanitize(dict(record))
    clean.setdefault("timestamp",_now())
    with p.open("a",encoding="utf-8") as f:
        f.write(json.dumps(clean,ensure_ascii=False,separators=(",",":"))+"\n")
    lines=p.read_text(encoding="utf-8").splitlines()
    if len(lines)>MAX_ENTRIES:
        p.write_text("\n".join(lines[-MAX_ENTRIES:])+"\n",encoding="utf-8")
    return clean

def load_history(limit=100):
    p=history_file()
    if not p.exists():
        return []
    out=[]
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            out.append(sanitize(json.loads(line)))
        except Exception:
            continue
    return out[-max(0,int(limit)):][::-1]

def latest_for_model(model_id):
    for row in load_history(MAX_ENTRIES):
        if row.get("model_id")==model_id:
            return row
    return None
