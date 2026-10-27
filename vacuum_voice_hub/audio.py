import shutil, subprocess, os, sys
from pathlib import Path

def ffmpeg_bin():
    bundled=Path(getattr(sys,"_MEIPASS",Path(__file__).parent))/('ffmpeg.exe' if os.name=='nt' else 'ffmpeg')
    if getattr(sys,"frozen",False) and bundled.is_file():return str(bundled)
    override=os.environ.get("VVH_FFMPEG")
    if override:
        candidate=Path(override).expanduser().resolve(strict=True)
        if not candidate.is_file():raise ValueError("VVH_FFMPEG must name an executable file")
        return str(candidate)
    p=shutil.which("ffmpeg")
    if p: return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def normalize(src: Path, dst: Path, codec="ogg"):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if codec=="ogg": args=["-c:a","libvorbis","-q:a","2"]
    elif codec=="mp3": args=["-c:a","libmp3lame","-b:a","24k"]
    elif codec=="wav": args=["-c:a","pcm_s16le"]
    else: raise ValueError(codec)
    cmd=[ffmpeg_bin(),"-hide_banner","-loglevel","error","-y","-i",str(src),"-vn","-ac","1","-ar","16000",*args,str(dst)]
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode: raise RuntimeError(p.stderr.strip())
    if not dst.exists() or dst.stat().st_size<128: raise RuntimeError(f"empty output: {dst}")
