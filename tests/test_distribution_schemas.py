import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_distribution_schema_contracts():
    release=json.loads((ROOT/"schemas"/"vvh.release-manifest.v1.schema.json").read_text())
    feed=json.loads((ROOT/"schemas"/"vvh.update-feed.v1.schema.json").read_text())
    assert release["properties"]["schema"]["const"]=="vvh.release-manifest.v1"
    assert feed["properties"]["schema"]["const"]=="vvh.update-feed.v1"
    assert "signature" in release["required"]
    assert "release_manifest" in feed["required"]
