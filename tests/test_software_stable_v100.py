"""Stable source release invariants are not physical robot certifications."""
import json
import subprocess
import sys
from pathlib import Path

from vacuum_voice_hub import __version__
from vacuum_voice_hub.catalog import models, voices
from vacuum_voice_hub.script_packs import list_locales


def test_release_software_stable_baseline():
    assert __version__.startswith("1.")
    assert len(models()) >= 223
    assert len(voices()) == 55
    assert len(list_locales()) >= 22
    assert [m["id"] for m in models() if m.get("device_tested")] == ["dreame.vacuum.r2209"]


def test_stable_source_audit_is_machine_readable_and_non_authorizing():
    root = Path(__file__).resolve().parents[1]
    run = subprocess.run([sys.executable, "scripts/stable_release_audit.py"],
                         cwd=root, capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr + run.stdout
    report = json.loads(run.stdout)
    assert report["schema"] == "vvh.software-stable-audit.v1"
    assert report["ok"] is True
    assert report["physical_compatibility_certified_by_this_audit"] is False
    assert report["new_custom_voice_transports_authorized"] is False
    assert report["community_hardware_tests_separate"] is True
    assert not report["errors"]
