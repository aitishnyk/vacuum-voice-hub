import tarfile
from pathlib import Path
from vacuum_voice_hub.compatibility import report_dir,merge_fallback
from vacuum_voice_hub.models.dreame_numeric import package

def _touch_events(root:Path,ids):
    root.mkdir(parents=True,exist_ok=True)
    for event_id in ids:
        (root/f"{event_id}.ogg").write_bytes(f"event-{event_id}".encode())

def test_x10_profile_is_conservative_106_event_set(tmp_path):
    p=tmp_path/"p";_touch_events(p,[0,7,11,12,45,999])
    r=report_dir(p,"dreame.vacuum.r2209")
    assert r["known_total"]==106
    assert r["covered"]==5
    assert r["extra_ids"]==[999]
    assert 999 not in r["covered_ids"]
    assert r["profile_hardware_verified"] is True

def test_category_coverage_and_semantic_missing_core_are_reported(tmp_path):
    p=tmp_path/"p";_touch_events(p,[7,11,35])
    r=report_dir(p,"dreame.vacuum.r2209")
    assert "cleaning" in r["category_coverage"]
    assert "error" in r["category_coverage"]
    assert all("semantic" in x and "category" in x for x in r["missing_core_events"])

def test_fallback_fills_only_known_missing_events(tmp_path):
    primary=tmp_path/"primary";fallback=tmp_path/"fallback"
    _touch_events(primary,[7,11]);_touch_events(fallback,[12,13,999])
    added=merge_fallback(primary,fallback,"dreame.vacuum.r2209")
    assert added==[12,13]
    assert (primary/"12.ogg").exists()
    assert not (primary/"999.ogg").exists()

def test_category_fallback_only_fills_requested_semantic_category(tmp_path):
    primary=tmp_path/"primary";fallback=tmp_path/"fallback"
    _touch_events(primary,[7])
    _touch_events(fallback,[12,13,35,45])
    added=merge_fallback(primary,fallback,"dreame.vacuum.r2209",categories={"error"})
    assert added==[35]
    assert (primary/"35.ogg").exists()
    assert not (primary/"13.ogg").exists()
    assert not (primary/"45.ogg").exists()

def test_package_filters_unknown_event_ids(tmp_path):
    src=tmp_path/"src";_touch_events(src,[0,7,11,12,13,999])
    out=tmp_path/"voice.tar.gz"
    meta=package(src,out,allowed_ids={0,7,11,12,13})
    assert meta["events"]==5
    assert meta["event_ids"]==[0,7,11,12,13]
    with tarfile.open(out,"r:gz") as tf:
        assert set(tf.getnames())=={"0.ogg","7.ogg","11.ogg","12.ogg","13.ogg"}
