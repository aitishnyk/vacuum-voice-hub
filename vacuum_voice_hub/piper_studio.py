"""Offline Piper neural TTS into unlicensed, reviewable Creator workspaces.

Only pre-existing local ONNX + JSON config files accepted. No voice download,
network calls, shell interpolation, robot commands or automatic pack install.
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from .audio_qa import inspect_wav
from .creator import PACK_ID_RE, assign_audio, default_workspace, new_workspace
from .script_packs import script_for_model

MAX_MODEL_BYTES = 500 * 1024 * 1024
MAX_CONFIG_BYTES = 256 * 1024


def _local_voice(model_path, locale):
    path = Path(model_path).expanduser().resolve(strict=True)
    if not path.is_file() or path.suffix.lower() != ".onnx":
        raise ValueError("Piper voice must be an existing local .onnx file")
    if path.stat().st_size <= 0 or path.stat().st_size > MAX_MODEL_BYTES:
        raise ValueError("Piper voice model exceeds 500 MiB or is empty")
    config = Path(str(path) + ".json")
    if not config.is_file() or config.stat().st_size > MAX_CONFIG_BYTES:
        raise ValueError("matching local .onnx.json configuration required (<=256 KiB)")
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("invalid Piper configuration JSON") from exc
    if not isinstance(data, dict) or not isinstance(data.get("language"), dict):
        raise ValueError("Piper configuration must contain a language object")
    lang = (data.get("language") or {}).get("code")
    if not isinstance(lang, str) or lang.split("_")[0].split("-")[0].lower() != locale.split("-")[0].lower():
        raise ValueError("Piper voice config language does not match script locale")
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(65536):
            sha.update(block)
    return path, config, lang, sha.hexdigest()


def synthesize_piper_workspace(locale, model_id, pack_id, author, voice_model, *,
                               output=None, speaker=None, allow_synthetic=False, overlay_path=None, lexicon_path=None):
    """Generate local Piper WAVs. Always requires explicit user opt-in."""
    if not allow_synthetic:
        raise PermissionError("explicit --allow-synthetic is required")
    if not PACK_ID_RE.fullmatch(pack_id or ""):
        raise ValueError("invalid Creator pack id")
    if not isinstance(author, str) or not author.strip() or len(author) > 128:
        raise ValueError("author required (max 128 characters)")
    if speaker is not None and (type(speaker) is not int or not 0 <= speaker <= 255):
        raise ValueError("speaker must be an integer 0..255")
    from .pronunciation import load_lexicon, pronounce
    script = script_for_model(locale, model_id, overlay_path)
    lexicon = load_lexicon(lexicon_path, locale) if lexicon_path is not None else None
    path, config, voice_locale, voice_sha = _local_voice(voice_model, locale)
    exe = shutil.which("piper")
    if not exe:
        raise RuntimeError("Piper executable not installed; no files were created")
    root = Path(output).expanduser().resolve() if output else default_workspace(pack_id)
    if root.exists():
        raise FileExistsError(f"Creator workspace already exists: {root}")
    root.parent.mkdir(parents=True, exist_ok=True)
    # mkdir with exist_ok=False prevents overwriting user files, including races.
    root.mkdir()
    try:
        new_workspace(root, pack_id=pack_id, name=f"{locale} Piper synthetic voice",
                      author=author, language=locale, license_name="UNLICENSED",
                      description="Local Piper synthesis. Voice licensing, speaker pronunciation and redistribution unreviewed.")
        qa = []
        for row in script["entries"]:
            wav = root / "audio" / (row["semantic"].replace("/", "_") + ".wav")
            cmd = [exe, "--model", str(path), "--config", str(config),
                   "--output_file", str(wav)]
            if speaker is not None:
                cmd += ["--speaker", str(speaker)]
            try:
                subprocess.run(cmd, input=pronounce(row["text"], lexicon)+"\n", text=True,
                               capture_output=True, check=True, timeout=40)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                raise RuntimeError(f"Piper failed for {row['semantic']}") from exc
            if not wav.is_file() or wav.stat().st_size > 25 * 1024 * 1024:
                raise RuntimeError(f"Piper produced missing/oversized WAV for {row['semantic']}")
            try:
                info = inspect_wav(wav)
            except ValueError as exc:
                raise RuntimeError(f"Piper generated invalid PCM WAV for {row['semantic']}") from exc
            qa.append({"semantic": row["semantic"], "warnings": info["warnings"],
                       "duration_sec": info["duration_sec"]})
            assign_audio(root, row["semantic"], wav, copy=False)
        return {
            "workspace": str(root), "engine": "piper-local",
            "model_id": script["model_id"], "locale": locale, "voice_locale": voice_locale,
            "voice_model_sha256": voice_sha, "speaker": speaker,
            "events_synthesized": len(qa), "mapped_model_semantics": script["mapped_count"],
            "overlay_count": script["overlay_count"], "translation_review_required": True,
            "pronunciation_lexicon_sha256": lexicon["sha256"] if lexicon else None,
            "qa": qa, "audio_files_generated": True,
            "redistribution_verified": False, "license_review_required": True,
            "install_authorized": False,
        }
    except BaseException:
        shutil.rmtree(root)
        raise
