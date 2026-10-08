import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_voicepack_v1_schema_contract():
    p=ROOT/"schemas"/"vvh.voicepack.v1.schema.json"
    doc=json.loads(p.read_text())
    assert doc["properties"]["schema"]["const"]=="vvh.voicepack.v1"
    assert set(["schema","id","name","author","language","adult","license","events"]).issubset(doc["required"])
    assert doc["properties"]["events"]["minProperties"]==1
