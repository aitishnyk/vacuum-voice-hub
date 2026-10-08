import json
from .paths import catalog_dir

def _load(name):
    return json.loads((catalog_dir()/name).read_text(encoding="utf-8"))

def voices(): return _load("voices.json")["voices"]
def models(): return _load("models.json")["models"]
def backlog(): return _load("research-backlog.json")["items"]
def events(): return _load("events.json")["events"]
def event_profiles(): return _load("event_profiles.json")["profiles"]
def bridge(): return _load("bridge_r2567r_to_dreame.json")["mapping"]
def ijai_map(): return _load("ijai_named_to_r2567r.json")["mapping"]
def roborock_map(): return _load("roborock_named_to_dreame.json")["mapping"]

def voice_by_id(voice_id):
    for v in voices():
        if v["id"] == voice_id: return v
    raise KeyError(f"Unknown voice: {voice_id}")

def model_by_id(model_id):
    for m in models():
        if model_id == m["id"] or model_id in m.get("aliases",[]): return m
    raise KeyError(f"Unsupported model: {model_id}")

def event_profile_for_model(model_id):
    model=model_by_id(model_id)
    profile_id=model.get("event_profile")
    for p in event_profiles():
        if p["id"]==profile_id: return p
    raise KeyError(f"No event profile {profile_id!r} for {model_id}")
