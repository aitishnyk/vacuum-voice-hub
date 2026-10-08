from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_catalog_package_data_synced():
    for src in (ROOT/'catalog').glob('*.json'):
        assert (ROOT/'vacuum_voice_hub'/'data'/src.name).read_bytes()==src.read_bytes()
