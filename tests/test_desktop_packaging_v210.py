"""Publishing must never bundle a codec that declares itself nonredistributable."""
import pytest
from scripts import build_desktop

@pytest.mark.parametrize('license_text',['configuration: --enable-nonfree','This binary is not legally redistributable.'])
def test_nonfree_codec_refused_before_pyinstaller(tmp_path,monkeypatch,license_text):
    codec=tmp_path/'ffmpeg';codec.write_bytes(b'fake')
    monkeypatch.setenv('VVH_FFMPEG',str(codec))
    monkeypatch.setattr(build_desktop.subprocess,'check_output',lambda *a,**k:license_text)
    with pytest.raises(SystemExit,match='nonredistributable'):build_desktop.main()
