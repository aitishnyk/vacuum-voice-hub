"""v2.0 software-only integration acceptance remains non-authorizing."""
import json
import subprocess
import sys
from pathlib import Path

from vacuum_voice_hub import __version__


def test_universal_studio_source_release_acceptance():
    root = Path(__file__).resolve().parents[1]
    run = subprocess.run(
        [sys.executable, "scripts/v2_release_acceptance.py"],
        cwd=root, capture_output=True, text=True, timeout=40
    )
    assert run.returncode == 0, run.stdout + run.stderr
    result = json.loads(run.stdout)
    assert result["schema"] == "vvh.v2-source-acceptance.v1"
    assert result["version"] == "2.0.0" == __version__
    assert result["ok"] is True
    assert result["required_feature_count"] >= 10
    assert result["all_required_feature_modules_importable"] is True
    assert result["model_profiles"] >= 223
    assert result["credited_voice_variants"] == 55
    assert result["text_only_script_locales"] >= 22
    assert result["physical_device_install_compatibility_certified"] is False
    assert result["desktop_code_signing_verified"] is False
    assert result["rights_independently_verified"] is False
