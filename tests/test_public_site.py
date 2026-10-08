import json
from pathlib import Path
from vacuum_voice_hub.sitegen import build_site,verify_site

def test_public_site_build_is_deterministic_and_complete(tmp_path):
    a=tmp_path/"a";b=tmp_path/"b"
    ra=build_site(a);rb=build_site(b)
    assert ra["schema"]=="vvh.public-catalog.v1"
    assert ra["voices"]>=55
    assert ra["models"]>=7
    for name in ["index.html","catalog.json","models.json","manifest.json"]:
        assert (a/name).read_bytes()==(b/name).read_bytes()
    manifest=json.loads((a/"manifest.json").read_text())
    assert manifest["counts"]["voices"]>=55
    assert manifest["counts"]["models"]>=7
    assert manifest["counts"]["hardware_verified_models"]==1
    assert verify_site(a)["ok"] is True

def test_public_catalog_is_sanitized_and_credits_first(tmp_path):
    out=tmp_path/"site";build_site(out)
    catalog=json.loads((out/"catalog.json").read_text())
    assert catalog["voices"]
    for v in catalog["voices"]:
        assert v["credit"]
        assert v["source_page"]
        assert "source" not in v
        assert "token" not in json.dumps(v).lower()
    models=json.loads((out/"models.json").read_text())
    x10=next(m for m in models["models"] if m["id"]=="dreame.vacuum.r2209")
    assert x10["device_tested"] is True
    assert x10["profile_hardware_verified"] is True

def test_public_site_verify_detects_tampering(tmp_path):
    out=tmp_path/"site";build_site(out)
    (out/"catalog.json").write_text("{}")
    v=verify_site(out)
    assert v["ok"] is False
    assert any("sha256 mismatch" in e for e in v["errors"])

def test_public_site_html_has_search_models_and_adult_gate(tmp_path):
    out=tmp_path/"site";build_site(out)
    html=(out/"index.html").read_text()
    assert 'id="q"' in html
    assert 'id="adult"' in html
    assert 'id="modelGrid"' in html
    assert "Hardware verified" in html or "hardware verified" in html
