import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_public_catalog_schema_contract():
    doc=json.loads((ROOT/"schemas"/"vvh.public-catalog.v1.schema.json").read_text())
    assert doc["properties"]["schema"]["const"]=="vvh.public-catalog.v1"
    assert set(["schema","version","files","counts"]).issubset(doc["required"])
