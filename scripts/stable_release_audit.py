#!/usr/bin/env python3
"""v1.0 software-only stable baseline audit; never certifies physical devices.

Run from checkout: python scripts/stable_release_audit.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vacuum_voice_hub import __version__  # noqa: E402
from vacuum_voice_hub.catalog import (models, voices, model_by_id,
                                     event_profile_for_model)  # noqa: E402
from vacuum_voice_hub.script_packs import list_locales, script_for_model  # noqa: E402
from vacuum_voice_hub.models.registry import get as adapter_for_model  # noqa: E402


def audit():
    errors = []
    def check(claim, error):
        if not claim:
            errors.append(error)

    mm = models()
    vv = voices()
    langs = list_locales()
    check(__version__ == "1.0.0", "version is not v1.0.0")
    check(len(mm) >= 223, "loss of v0.20 model identities")
    check(len(vv) == 55, "55 attributed v0.19 voice variants not preserved")
    check(len(langs) >= 22, "loss of v0.20 text script locales")
    check(len({m["id"] for m in mm}) == len(mm), "duplicated model ID")
    check(len({v["id"] for v in vv}) == len(vv), "duplicated voice ID")
    check(sum(bool(m.get("device_tested")) for m in mm) == 1,
          "hardware verification changed without independently accepted evidence")
    check([m["id"] for m in mm if m.get("device_tested")] == ["dreame.vacuum.r2209"],
          "X10 physical verification baseline drift")

    catalog = (ROOT / "catalog/models.json").read_bytes()
    runtime = (ROOT / "vacuum_voice_hub/data/models.json").read_bytes()
    check(catalog == runtime, "packaged model registry mirror differs")

    original = json.loads((ROOT / "tests/fixtures/v08_model_identity.json").read_text("utf-8"))
    previous = json.loads((ROOT / "tests/fixtures/v012_model_identity.json").read_text("utf-8"))
    for label, fixture in (("v0.8", original), ("v0.12", previous)):
        for row in fixture["models"]:
            try:
                model = model_by_id(row["id"])
                check(model["id"] == row["id"], label + " ID changed: " + row["id"])
                for alias in row["aliases"]:
                    check(model_by_id(alias)["id"] == row["id"],
                          label + " alias changed: " + alias)
            except KeyError:
                errors.append(label + " missing identity: " + row["id"])

    seen_aliases = {}
    for model in mm:
        key = model["id"]
        for alias in model.get("aliases", []):
            previous_id = seen_aliases.setdefault(alias, key)
            check(previous_id == key, "alias collision: " + alias)
        try:
            profile = event_profile_for_model(key)
            check(len(profile["known_event_ids"]) >= 5, key + " no mapping evidence")
            adapter = adapter_for_model(key)
            check(callable(adapter.package), key + " missing package adapter")
        except (KeyError, ValueError, AttributeError) as exc:
            errors.append("adapter/event profile unavailable " + key + ": " + str(exc))
        if model.get("transport", {}).get("kind") in ("unsupported-local", "signed-official-only"):
            check(not model["transport"].get("allow_default"),
                  "unsupported/signed-only install accidentally enabled: " + key)
        if key in set(json.loads(catalog)["expansion"].get("added_model_ids_v020", [])):
            check(model.get("device_tested") is False and
                  model.get("transport", {}).get("kind") == "unsupported-local",
                  "v0.20 identity auto-promoted to install: " + key)

    for locale in langs:
        check(locale["prerecorded"] is False,
              "text script falsely claims recorded audio: " + locale["locale"])
        check(locale["scripted_events"] >= 16,
              "missing core translation events: " + locale["locale"])
        try:
            report = script_for_model(locale["locale"], "dreame.vacuum.r2209")
            check(report["prerecorded"] is False and
                  report["model_install_authorized"] is False,
                  "script authorized install or recording: " + locale["locale"])
        except (KeyError, ValueError) as exc:
            errors.append("failed script locale " + locale["locale"] + ": " + str(exc))

    return {
        "schema": "vvh.software-stable-audit.v1",
        "version": __version__, "ok": not errors,
        "errors": sorted(set(errors)),
        "models": len(mm), "voices": len(vv),
        "text_script_locales": len(langs),
        "hardware_verified_models": 1 if not errors else
            sum(bool(m.get("device_tested")) for m in mm),
        "physical_compatibility_certified_by_this_audit": False,
        "new_custom_voice_transports_authorized": False,
        "community_hardware_tests_separate": True,
    }


if __name__ == "__main__":
    report = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if report["ok"] else 1)
