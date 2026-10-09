"""Local, attributed pronunciation replacements for opt-in offline TTS only.

Written translations are immutable. An unreviewed phonetic hint never certifies
language, speaker rights, robot compatibility or package install permission.
"""
import hashlib
import json
import re
from pathlib import Path

from .translation_overlays import _no_duplicate_keys
from .script_packs import list_locales, script_for_model

SCHEMA = "vvh.pronunciation-lexicon.v1"
MAX_BYTES = 65536


def _valid_text(text):
    return (isinstance(text, str) and 1 <= len(text) <= 160
            and text.strip() == text
            and not any(ord(c) < 32 or ord(c) == 127 for c in text))


def load_lexicon(path, locale):
    source = Path(path).expanduser()
    if source.is_symlink() or not source.is_file():
        raise ValueError("lexicon must be an existing regular local file")
    with source.open("rb") as inp:
        data = inp.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("lexicon exceeds 64 KiB")
    try:
        doc = json.loads(data.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid lexicon JSON") from exc
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise ValueError("unsupported lexicon schema")
    if doc.get("locale") != locale or locale not in {row["locale"] for row in list_locales()}:
        raise ValueError("lexicon locale mismatch")
    for field in ("author", "license"):
        if not _valid_text(doc.get(field)) or len(doc[field]) > 128:
            raise ValueError("lexicon " + field + " required")
    if doc.get("source_url") is not None:
        from urllib.parse import urlsplit
        url = doc["source_url"]
        if not isinstance(url, str) or len(url) > 2048:
            raise ValueError("invalid lexicon source URL")
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("lexicon source must be HTTPS")
    entries = doc.get("entries")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 128:
        raise ValueError("lexicon needs 1..128 substitutions")
    keys = set()
    output = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"written", "spoken"}:
            raise ValueError("invalid lexicon entry")
        written, spoken = entry["written"], entry["spoken"]
        if not _valid_text(written) or not _valid_text(spoken) or written == spoken:
            raise ValueError("invalid pronunciation substitution")
        if written.casefold() in keys:
            raise ValueError("duplicate lexicon source term")
        keys.add(written.casefold())
        output.append({"written": written, "spoken": spoken})
    return {"schema": SCHEMA, "locale": locale, "author": doc["author"],
            "license": doc["license"], "entries": output,
            "sha256": hashlib.sha256(data).hexdigest(),
            "independent_language_review": False, "install_authorized": False}


def pronounce(text, lexicon):
    if lexicon is None:
        return text
    if not isinstance(text, str):
        raise ValueError("pronunciation source must be a string")
    mapping = {row["written"]: row["spoken"] for row in lexicon["entries"]}
    pattern = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(key) for key in
                         sorted(mapping, key=lambda k: (-len(k), k))) + r")(?!\w)")
    # Single substitution pass: replacement text cannot trigger another rule.
    return pattern.sub(lambda match: mapping[match.group()], text)


def pronunciation_preview(locale, model_id, lexicon_path, *, overlay_path=None):
    lexicon = load_lexicon(lexicon_path, locale)
    script = script_for_model(locale, model_id, overlay_path)
    rows = [{"semantic": row["semantic"], "source": row["text"],
             "tts_input": pronounce(row["text"], lexicon),
             "event_ids": row["target_event_ids"]} for row in script["entries"]]
    return {"schema": SCHEMA, "model_id": script["model_id"], "locale": locale,
            "lexicon_sha256": lexicon["sha256"],
            "rows": rows, "modified": sum(r["source"] != r["tts_input"] for r in rows),
            "base_translations_changed": False,
            "native_language_review_verified": False,
            "audio_files_generated": False, "install_authorized": False}
