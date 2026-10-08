import json
from pathlib import Path
from vacuum_voice_hub.release import build_release,verify_release

EPOCH=1700000000

def test_release_bundle_is_reproducible(tmp_path):
    a=tmp_path/"a";b=tmp_path/"b"
    ra=build_release(a,EPOCH);rb=build_release(b,EPOCH)
    assert ra["verified"] is True
    assert rb["verified"] is True
    names=sorted(p.name for p in a.iterdir())
    assert names==sorted(p.name for p in b.iterdir())
    for name in names:
        assert (a/name).read_bytes()==(b/name).read_bytes(),name
    verified=verify_release(a)
    assert verified["ok"] is True
    assert verified["signature_status"]=="unsigned"

def test_release_manifest_and_feed_are_linked(tmp_path):
    out=tmp_path/"release";build_release(out,EPOCH)
    manifest=json.loads((out/"release-manifest.json").read_text())
    feed=json.loads((out/"update-feed.json").read_text())
    assert manifest["schema"]=="vvh.release-manifest.v1"
    assert feed["schema"]=="vvh.update-feed.v1"
    assert manifest["version"]==feed["current_version"]
    assert manifest["signature"]["status"]=="unsigned"
    assert manifest["desktop_builds"]["hashes_in_this_manifest"] is False
    assert feed["public_bundle"]["name"] in manifest["artifacts"]

def test_release_verify_detects_tampering(tmp_path):
    out=tmp_path/"release";build_release(out,EPOCH)
    manifest=json.loads((out/"release-manifest.json").read_text())
    bundle=next(name for name,meta in manifest["artifacts"].items() if meta["type"]=="public-catalog-bundle")
    with (out/bundle).open("ab") as f:f.write(b"tamper")
    v=verify_release(out)
    assert v["ok"] is False
    assert any("mismatch" in e for e in v["errors"])

def test_sha256sums_does_not_claim_self_hash(tmp_path):
    out=tmp_path/"release";build_release(out,EPOCH)
    sums=(out/"SHA256SUMS").read_text()
    assert "release-manifest.json" in sums
    assert "update-feed.json" in sums
    assert "sbom.spdx.json" in sums
    assert "SHA256SUMS" not in sums
