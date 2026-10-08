from vacuum_voice_hub.formats.registry import ADAPTERS

def test_v02_source_adapters_registered():
    assert "dreame-canonical-ogg" in ADAPTERS
    assert "robovoice-r2567r-mp3" in ADAPTERS
    assert "ijai-named-mp3" in ADAPTERS
    assert "roborock-pkg" in ADAPTERS
