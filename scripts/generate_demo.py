#!/usr/bin/env python3
"""Regenerate CC0 speech with eSpeak NG and bundled FFmpeg; runtime needs neither TTS nor internet."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from vacuum_voice_hub.audio import ffmpeg_bin
ROOT=Path(__file__).resolve().parents[1]/'vacuum_voice_hub'/'demo_assets'
EVENTS=[('clean.start','Cleaning started.'),('clean.pause','Cleaning paused.'),('clean.complete','Cleaning completed.'),('dock.return.charge','Returning to charging dock.'),('dock.charging','Charging started.'),('error.main_brush','Main brush needs attention.'),('battery.low','Battery low.'),('clean.complete','Task completed successfully.')]
def main():
    ROOT.mkdir(exist_ok=True)
    records=[]
    with tempfile.TemporaryDirectory() as td:
        for i,(semantic,text) in enumerate(EVENTS):
            name=f'{i+1:02d}.wav'
            raw=Path(td)/name
            subprocess.run(['espeak-ng','-v','en-us','-s','155','-w',str(raw),text],check=True)
            subprocess.run([ffmpeg_bin(),'-v','error','-y','-i',str(raw),'-ac','1','-ar','16000','-c:a','pcm_s16le',str(ROOT/name)],check=True)
            records.append(dict(file=name,semantic=semantic,text=text,sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()))
    (ROOT/'manifest.json').write_text(json.dumps({'schema':'vvh.demo-assets.v1','license':'CC0-1.0','generator':'eSpeak NG 1.52.0 en-us, 155 words/minute; FFmpeg mono PCM16 16kHz','events':records},indent=2)+'\n')
if __name__=='__main__':main()
