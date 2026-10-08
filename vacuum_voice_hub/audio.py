import shutil, subprocess
from pathlib import Path

def ffmpeg_bin():
    p=shutil.which("ffmpeg")
    if p: return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def normalize(src: Path, dst: Path, codec="ogg"):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if codec=="ogg": args=["-c:a","libvorbis","-q:a","2"]
    elif codec=="mp3": args=["-c:a","libmp3lame","-b:a","16k"]
    else: raise ValueError(codec)
    cmd=[ffmpeg_bin(),"-hide_banner","-loglevel","error","-y","-i",str(src),"-vn","-ac","1","-ar","16000",*args,str(dst)]
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode: raise RuntimeError(p.stderr.strip())
    if not dst.exists() or dst.stat().st_size<128: raise RuntimeError(f"empty output: {dst}")
