SERVICE="VacuumVoiceHub"

def _keyring():
    try:
        import keyring
        return keyring
    except Exception as e:
        raise RuntimeError("keyring support is not installed; install vacuum-voice-hub[security]") from e

def save(name,token):
    if not name or not name.strip():
        raise ValueError("credential name is required")
    token=(token or "").strip()
    if len(token)!=32 or any(c not in "0123456789abcdefABCDEF" for c in token):
        raise ValueError("token must be exactly 32 hexadecimal characters")
    _keyring().set_password(SERVICE,name.strip(),token)
    return {"name":name.strip(),"stored":True}

def load(name):
    token=_keyring().get_password(SERVICE,name)
    if not token:
        raise KeyError(f"credential not found: {name}")
    return token

def status(name):
    return {"name":name,"stored":bool(_keyring().get_password(SERVICE,name))}

def delete(name):
    kr=_keyring()
    try:
        kr.delete_password(SERVICE,name)
        deleted=True
    except Exception:
        deleted=False
    return {"name":name,"deleted":deleted}
