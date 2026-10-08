"""Localized, model-aware recording scripts and optional offline synthetic audio.

Script packs contain only text: never treat a locale as a prerecorded voice.
Synthesis requires installed espeak-ng and explicit opt-in. No cloud calls.
"""
import json
import os
import re
import shutil
import subprocess
from importlib.resources import files
from pathlib import Path

from .catalog import event_by_semantic, event_profile_for_model, model_by_id

SCHEMA = "vvh.script-pack.v1"
VOICE_RE = re.compile(r"^[a-zA-Z0-9_+.-]{1,64}$")


def _data():
    doc = json.loads((files("vacuum_voice_hub") / "data" / "script_templates.json").read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA:
        raise ValueError("unsupported script-pack schema")
    return doc


def list_locales():
    doc = _data()
    return [
        {"locale": key, "name": value["name"], "scripted_events": len(value["phrases"]),
         "prerecorded": False, "requires_voice_engine_for_audio": True}
        for key, value in sorted(doc["locales"].items())
    ]


def script_for_model(locale, model_id):
    doc = _data()
    if locale not in doc["locales"]:
        raise ValueError(f"unknown script locale: {locale}")
    model = model_by_id(model_id)
    profile = event_profile_for_model(model["id"])
    allowed = set(profile["known_event_ids"])
    translations = doc["locales"][locale]["phrases"]
    rows = []
    for semantic in doc["semantics"]:
        phrase = translations.get(semantic)
        if not isinstance(phrase, str) or not phrase.strip():
            raise ValueError(f"missing script phrase: {locale}/{semantic}")
        ids = sorted({int(e["id"]) for e in event_by_semantic(semantic)
                      if int(e["id"]) in allowed})
        rows.append({"semantic": semantic, "text": phrase, "target_event_ids": ids,
                     "mapped_to_model": bool(ids)})
    return {
        "schema": SCHEMA, "locale": locale, "language_name": doc["locales"][locale]["name"],
        "model_id": model["id"], "event_profile": profile["id"],
        "status": "text-only-not-audio-pack", "prerecorded": False,
        "model_install_authorized": False,
        "scripted_count": len(rows),
        "mapped_count": sum(bool(row["target_event_ids"]) for row in rows),
        "unmapped_semantics": [row["semantic"] for row in rows if not row["mapped_to_model"]],
        "entries": rows,
    }


def synthesize_workspace(locale, model_id, pack_id, author, voice, *,
                         output=None, speed=160, pitch=50, allow_synthetic=False):
    """Generate actual WAV files using local espeak-ng; never build/install automatically."""
    if not allow_synthetic:
        raise PermissionError("explicit --allow-synthetic is required")
    if not VOICE_RE.fullmatch(voice or ""):
        raise ValueError("invalid local espeak-ng voice identifier")
    if not isinstance(speed, int) or not 80 <= speed <= 300:
        raise ValueError("speed must be 80..300 words/min")
    if not isinstance(pitch, int) or not 0 <= pitch <= 99:
        raise ValueError("pitch must be 0..99")
    if not author or not author.strip() or len(author) > 128:
        raise ValueError("author is required (max 128 characters)")
    exe = shutil.which("espeak-ng")
    if not exe:
        raise RuntimeError("espeak-ng is not installed; only text scripts are available")
    from .creator import new_workspace, assign_audio, default_workspace
    script = script_for_model(locale, model_id)
    root = Path(output).expanduser().resolve() if output else default_workspace(pack_id)
    if root.exists():
        raise FileExistsError(f"creator workspace already exists: {root}")
    root.parent.mkdir(parents=True, exist_ok=True)
    # Creator stores each semantic WAV as an ordinary reusable voice project.
    root.mkdir()
    try:
        new_workspace(root, pack_id=pack_id, name=f"{locale} local synthetic voice",
                      author=author, language=locale, license_name="UNLICENSED",
                      description="Locally synthesized with espeak-ng; unreviewed and not endorsed for redistribution.")
        for row in script["entries"]:
            # Only mapped semantics are needed for this target, but the project remains portable.
            wav = root / "audio" / (row["semantic"].replace("/", "_") + ".wav")
            cmd = [exe, "-v", voice, "-s", str(speed), "-p", str(pitch),
                   "-w", str(wav), row["text"]]
            try:
                subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                raise RuntimeError(f"local synthesis failed for {row['semantic']}") from exc
            if not wav.is_file() or wav.stat().st_size == 0:
                raise RuntimeError(f"no audio synthesized for {row['semantic']}")
            assign_audio(root, row["semantic"], wav, copy=False)
        return {
            "workspace": str(root), "locale": locale, "model_id": script["model_id"],
            "events_synthesized": script["scripted_count"],
            "mapped_model_semantics": script["mapped_count"],
            "engine": "espeak-ng", "engine_voice": voice,
            "audio_files_generated": True, "redistribution_verified": False,
            "install_authorized": False,
            "next_step": f"vvh creator build {root} --model {script['model_id']}"
        }
    except Exception:
        shutil.rmtree(root)
        raise
