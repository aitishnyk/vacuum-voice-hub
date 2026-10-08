import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_bridge_has_core_events():
    m=json.loads((ROOT/'catalog/bridge_r2567r_to_dreame.json').read_text())['mapping']
    assert m['006']==7
    assert m['007']==11
    assert len(m)>=70
