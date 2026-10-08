import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_catalog_unique_ids():
    d=json.loads((ROOT/'catalog/voices.json').read_text()); ids=[x['id'] for x in d['voices']]; assert len(ids)==len(set(ids)); assert len(ids)>=20

def test_every_voice_has_credit_source():
    d=json.loads((ROOT/'catalog/voices.json').read_text());
    for v in d['voices']:
        assert v.get('credit'); assert v.get('source',{}).get('page'); assert v.get('source',{}).get('size',0)>0

def test_model_r2209_present():
    d=json.loads((ROOT/'catalog/models.json').read_text()); assert any(x['id']=='dreame.vacuum.r2209' for x in d['models'])
