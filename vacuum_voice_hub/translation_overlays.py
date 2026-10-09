"""Opt-in community translation overlays for any catalog semantic event.

Local text data only. An overlay never adds model IDs, vendor event IDs,
voice audio, install permissions or claims that translations are reviewed.
"""
import json
from pathlib import Path
from urllib.parse import urlsplit

from .catalog import events, event_profile_for_model, model_by_id

SCHEMA = "vvh.translation-overlay.v1"
MAX_BYTES = 128 * 1024
MAX_ENTRIES = 512
MAX_PHRASE_CHARS = 400


def _no_duplicate_keys(pairs):
    out = {}
    for key, val in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = val
    return out


def _phrase(value):
    return (isinstance(value, str) and value.strip() and
            len(value) <= MAX_PHRASE_CHARS and
            not any(ord(c) < 32 or ord(c) == 127 for c in value))


def load_overlay(path, locale):
    """Strictly validate a bounded local file before using text in synthesis."""
    with Path(path).expanduser().open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("translation overlay exceeds 128 KiB")
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid UTF-8 JSON overlay") from exc
    if not isinstance(obj, dict) or obj.get("schema") != SCHEMA:
        raise ValueError("unsupported translation overlay schema")
    if obj.get("locale") != locale:
        raise ValueError("translation overlay locale mismatch")
    author = obj.get("author")
    license_name = obj.get("license")
    if not isinstance(author, str) or not author.strip() or len(author) > 128:
        raise ValueError("translation author is required")
    if not isinstance(license_name, str) or not license_name.strip() or len(license_name) > 128:
        raise ValueError("translation license must be declared (UNLICENSED if unknown)")
    link = obj.get("source_url")
    if link is not None:
        if not isinstance(link, str) or len(link) > 2048:
            raise ValueError("invalid translation source URL")
        parsed = urlsplit(link)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("translation source must be HTTPS without credentials")
    phrases = obj.get("translations")
    if not isinstance(phrases, dict) or not phrases or len(phrases) > MAX_ENTRIES:
        raise ValueError("translations must have 1..512 entries")
    known = {e["semantic"] for e in events()}
    for semantic, value in phrases.items():
        if semantic not in known:
            raise ValueError(f"unknown semantic event: {semantic}")
        if not _phrase(value):
            raise ValueError(f"invalid translated phrase: {semantic}")
    return {"schema": SCHEMA, "locale": locale, "author": author,
            "license": license_name, "source_url": link, "translations": phrases,
            "reviewed": False, "audio_files_generated": False,
            "install_authorized": False}


def translation_scaffold(locale, model_id, limit=256):
    """Provide English reference text, never pretend it is a translation."""
    if type(limit) is not int or not 1 <= limit <= 512:
        raise ValueError("scaffold limit must be 1..512")
    from .script_packs import script_for_model
    base = script_for_model(locale, model_id)
    model = model_by_id(model_id)
    known = set(event_profile_for_model(model["id"])["known_event_ids"])
    supplied = {item["semantic"] for item in base["entries"]}
    group = {}
    for item in events():
        if item["semantic"] in supplied or int(item["id"]) not in known:
            continue
        description = item.get("description")
        if not isinstance(description, str) or not description.strip():
            continue
        row = group.setdefault(item["semantic"], {
            "semantic": item["semantic"],
            "english_reference_not_translated": description.strip(),
            "target_event_ids": [],
        })
        row["target_event_ids"].append(int(item["id"]))
    candidates = [group[k] for k in sorted(group)][:limit]
    return {
        "schema": SCHEMA, "locale": locale,
        "model_id": model["id"], "author": "REPLACE_WITH_TRANSLATOR_NAME",
        "license": "UNLICENSED", "source_url": None,
        "translations": {},
        "translation_candidates": candidates,
        "candidate_count": len(candidates), "core_script_count": len(base["entries"]),
        "note": "English reference text is NOT an existing localized translation. Fill translations with reviewed target-language phrases before importing.",
        "install_authorized": False, "audio_files_generated": False,
    }
