#!/usr/bin/env python3
"""v2.0 software-source acceptance; never physical hardware certification."""
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.stable_release_audit import audit
from vacuum_voice_hub import __version__
from vacuum_voice_hub.universal_studio import studio_capabilities

FEATURES = {
    "audio_ab": ("audio_compare", "compare_audio"),
    "language_review": ("language_review", "audit_language_review"),
    "pronunciation_lexicon": ("pronunciation", "load_lexicon"),
    "firmware_matrix": ("firmware_matrix", "firmware_matrix"),
    "visual_audio_timeline": ("audio_timeline", "audio_timeline"),
    "community_inbox": ("community_inbox", "audit_inbox"),
    "adapter_interchange": ("adapter_interchange", "verify_interchange"),
    "voice_library": ("voice_library", "audit_library"),
    "creator_recovery": ("creator_recovery", "verify_backup"),
    "integrated_studio": ("universal_studio", "inspect_studio"),
}


def acceptance():
    preservation = audit()
    cap = studio_capabilities()
    errors = list(preservation["errors"])
    if __version__ != "2.0.0":
        errors.append("expected exact 2.0.0 package version")
    if cap["model_profiles"] < 223 or cap["recorded_voice_variants"] != 55:
        errors.append("historical voice or model baseline regressed")
    if cap["text_script_locales"] < 22 or cap["physically_verified_models"] != 1:
        errors.append("text locale or physical evidence baseline changed")
    if any(cap[k] is not False for k in (
        "model_profiles_are_physical_installs",
        "text_locales_are_recordings",
        "hardware_install_authorized"
    )):
        errors.append("invalid universal hardware/text-voice claim")
    for feature, (module, function) in sorted(FEATURES.items()):
        try:
            implementation = importlib.import_module("vacuum_voice_hub." + module)
            if not callable(getattr(implementation, function, None)):
                errors.append("missing feature implementation: " + feature)
        except (ImportError, AttributeError, SyntaxError) as exc:
            errors.append("feature import failed: " + feature + ": " + str(exc))
    for path in (
        "docs/MIGRATION_V200.md",
        "docs/UNIVERSAL_STUDIO_V200.md",
        "docs/RELEASE_NOTES_V200.md",
        ".github/workflows/publish-stable-v200.yml",
    ):
        if not (ROOT / path).is_file():
            errors.append("required source release file missing: " + path)
    return {
        "schema": "vvh.v2-source-acceptance.v1",
        "version": __version__, "ok": not errors, "errors": errors,
        "model_profiles": cap["model_profiles"],
        "credited_voice_variants": cap["recorded_voice_variants"],
        "text_only_script_locales": cap["text_script_locales"],
        "required_feature_count": len(FEATURES),
        "all_required_feature_modules_importable": not any(
            "feature" in e for e in errors),
        "physical_device_install_compatibility_certified": False,
        "manufacturer_signature_verified": False,
        "desktop_code_signing_verified": False,
        "rights_independently_verified": False,
        "commercial_telegram_or_bunny_deployed": False,
    }


if __name__ == "__main__":
    report = acceptance()
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    raise SystemExit(0 if report["ok"] else 1)
