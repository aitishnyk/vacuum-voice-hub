import shutil, subprocess, tarfile
from pathlib import Path

LEGACY_ROBOROCK_KEY="r0ckrobo#23456"

def _ccrypt():
    return shutil.which("ccrypt") or shutil.which("ccencrypt") or shutil.which("ccat")

def decrypt_roborock_pkg(src: Path, dst: Path):
    """Decrypt the historical ccrypt-based Roborock voice package format."""
    exe=_ccrypt()
    if not exe:
        raise RuntimeError("Old Roborock .pkg support requires ccrypt. macOS: brew install ccrypt")
    if Path(exe).name=="ccat":
        cmd=[exe,"-k","-",str(src)]
        with open(dst,"wb") as out:
            p=subprocess.run(cmd,input=LEGACY_ROBOROCK_KEY+"\n",text=True,stdout=out,stderr=subprocess.PIPE)
    else:
        cmd=[exe,"-c","-k","-",str(src)]
        with open(dst,"wb") as out:
            p=subprocess.run(cmd,input=LEGACY_ROBOROCK_KEY+"\n",text=True,stdout=out,stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError("ccrypt failed: "+p.stderr.strip())
    if not tarfile.is_tarfile(dst):
        raise ValueError("decrypted .pkg is not a tar archive")
    return dst

def encrypt_roborock_pkg(src: Path, dst: Path):
    """Encrypt a tar.gz as the historical Roborock ccrypt .pkg format."""
    exe=shutil.which("ccrypt") or shutil.which("ccencrypt")
    if not exe:
        raise RuntimeError("Building classic Roborock .pkg requires ccrypt. macOS: brew install ccrypt")
    cmd=[exe,"-e","-K",LEGACY_ROBOROCK_KEY] if Path(exe).name=="ccrypt" else [exe,"-K",LEGACY_ROBOROCK_KEY]
    with open(src,"rb") as inp, open(dst,"wb") as out:
        p=subprocess.run(cmd,stdin=inp,stdout=out,stderr=subprocess.PIPE)
    if p.returncode:
        dst.unlink(missing_ok=True)
        raise RuntimeError("ccrypt encryption failed: "+p.stderr.decode(errors="replace").strip())
    if not dst.exists() or dst.stat().st_size<128:
        raise RuntimeError("ccrypt produced an empty Roborock package")
    return dst
