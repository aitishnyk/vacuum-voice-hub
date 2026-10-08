import shutil, subprocess, tarfile
from pathlib import Path

LEGACY_ROBOROCK_KEY="r0ckrobo#23456"

def decrypt_roborock_pkg(src: Path, dst: Path):
    """Decrypt the historical ccrypt-based Roborock voice package format."""
    exe=shutil.which("ccrypt") or shutil.which("ccat")
    if not exe:
        raise RuntimeError("Old Roborock .pkg support requires ccrypt. macOS: brew install ccrypt")
    if Path(exe).name=="ccat":
        cmd=[exe,"-k","-",str(src)]
    else:
        cmd=[exe,"-c","-k","-",str(src)]
    with open(dst,"wb") as out:
        p=subprocess.run(
            cmd,
            input=LEGACY_ROBOROCK_KEY+"\n",
            text=True,
            stdout=out,
            stderr=subprocess.PIPE,
        )
    if p.returncode:
        raise RuntimeError("ccrypt failed: "+p.stderr.strip())
    if not tarfile.is_tarfile(dst):
        raise ValueError("decrypted .pkg is not a tar archive")
    return dst
