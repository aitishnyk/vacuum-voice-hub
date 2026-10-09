"""v1.5 waveform previews and non-destructive exact selection export."""
import hashlib
import json
import math
import struct
import subprocess
import sys
import wave

import pytest

from vacuum_voice_hub.audio_timeline import audio_timeline, cut_preview


def fixture(tmp, name="tone.wav", seconds=2):
    path = tmp / name
    samples = [round(9000*math.sin(2*math.pi*320*n/16000))
               for n in range(round(seconds*16000))]
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(16000)
        wav.writeframes(struct.pack("<"+"h"*len(samples), *samples))
    return path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_waveform_bins_source_unchanged(tmp_path):
    src=fixture(tmp_path)
    sha=digest(src)
    info=audio_timeline(src,bins=64)
    assert info["schema"]=="vvh.audio-timeline.v1"
    assert info["bin_count"] == 64
    assert 0.2 < max(info["peak_bins"]) < 0.4
    assert info["duration_sec"] == 2
    assert info["source_sha256"] == sha == digest(src)
    assert not info["install_authorized"]


def test_cut_selected_500ms_to_new_file_only(tmp_path):
    src=fixture(tmp_path)
    sha=digest(src)
    out=tmp_path/"trim.wav"
    result=cut_preview(src,out,start_ms=250,end_ms=750,fade_ms=10)
    assert result["source_sha256"]==sha==digest(src)
    assert out.exists()
    with wave.open(str(out),"rb") as wav:
        assert wav.getframerate()==16000
        assert wav.getnframes()==8000
        assert wav.getnchannels()==1
    assert result["creator_manifest_changed"] is False
    assert result["human_review_required"] is True
    with pytest.raises(FileExistsError):
        cut_preview(src,out,start_ms=0,end_ms=1000)
    assert digest(out)==result["output_sha256"]


@pytest.mark.parametrize("start,end,fade", [
    (-1,500,8),(0,100,8),(500,500,8),(700,600,8),
    (0,3000,8),(0,1000,201),(float("nan"),700,0),
])
def test_unsafe_timeline_selection_fails(tmp_path,start,end,fade):
    src=fixture(tmp_path)
    with pytest.raises(ValueError):
        cut_preview(src,tmp_path/"never.wav",start_ms=start,end_ms=end,fade_ms=fade)
    assert not (tmp_path/"never.wav").exists()


def test_fail_closed_bad_bins_symlinks_and_empty_audio(tmp_path):
    src=fixture(tmp_path)
    with pytest.raises(ValueError,match="16..512"):
        audio_timeline(src,bins=0)
    symlink=tmp_path/"link.wav";symlink.symlink_to(src)
    with pytest.raises(ValueError,match="symlink"):
        audio_timeline(symlink)
    with pytest.raises(ValueError,match="symlink"):
        cut_preview(symlink,tmp_path/"never.wav",start_ms=0,end_ms=400)


def test_cli_waveform_and_cut_preview(tmp_path):
    src=fixture(tmp_path)
    result=subprocess.run([sys.executable,"-m","vacuum_voice_hub","creator",
                           "waveform",str(src),"--bins","32"],
                          capture_output=True,text=True,check=True)
    assert json.loads(result.stdout)["bin_count"] == 32
    out=tmp_path/"new-preview.wav"
    result=subprocess.run([sys.executable,"-m","vacuum_voice_hub","creator",
                           "cut-preview",str(src),"--start-ms","200",
                           "--end-ms","600","--output",str(out)],
                          capture_output=True,text=True,check=True)
    assert json.loads(result.stdout)["output_sha256"]==digest(out)


def test_creator_gui_contains_browser_local_timeline():
    from pathlib import Path
    html = (Path(__file__).resolve().parents[1] /
            "vacuum_voice_hub/web/creator.html").read_text(encoding="utf-8")
    for key in ("timelineFile", "timelineCanvas", "timelineLoad",
                "timelineStart", "timelineEnd", "timelineFade", "timelineExport"):
        assert 'id="'+key+'"' in html
    assert "new OfflineAudioContext(1,count,16000)" in html
    assert "getChannelData(0)" in html
    assert "audio/wav" in html
