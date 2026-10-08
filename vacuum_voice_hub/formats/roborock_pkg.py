from pathlib import Path
from ..archive import extract
from ..legacy_ccrypt import decrypt_roborock_pkg
from .roborock_named import adapt_dir

def adapt(source: Path, work: Path) -> dict:
    decrypted=work/"decrypted.tar.gz"
    raw=work/"raw"
    out=work/"canonical"
    decrypt_roborock_pkg(source,decrypted)
    extract(decrypted,raw)
    result=adapt_dir(raw,out)
    result["source_events"]=result.get("source_events",result.get("events"))
    return result
