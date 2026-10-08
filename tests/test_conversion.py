import shutil, tempfile, wave, math, struct, tarfile
from pathlib import Path
import pytest
from vacuum_voice_hub.local_import import convert_local


def _wav(path: Path, freq=440):
    rate=16000
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        frames=[]
        for i in range(rate//10):
            v=int(5000*math.sin(2*math.pi*freq*i/rate)); frames.append(struct.pack('<h',v))
        w.writeframes(b''.join(frames))

@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='ffmpeg unavailable')
def test_roborock_named_local_conversion(tmp_path):
    src=tmp_path/'named'; src.mkdir()
    for i,name in enumerate(['start.wav','pause.wav','home.wav','charging.wav','findme.wav','finish.wav']): _wav(src/name,440+i*30)
    out=tmp_path/'out.tar.gz'
    meta=convert_local(src,output=out)
    assert meta['detected']=='roborock-named'
    assert meta['events']>=5
    assert out.is_file()
    with tarfile.open(out,'r:gz') as tf:
        names=tf.getnames()
        assert '7.ogg' in names
        assert '11.ogg' in names
        assert '45.ogg' in names
