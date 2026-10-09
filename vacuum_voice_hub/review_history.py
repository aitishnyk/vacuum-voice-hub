"""Local hash-linked review decision journal.

Detects accidental/manual tampering and truncated entries within the current
file. NOT authenticated: someone who can rewrite files can forge the chain.
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "vvh.review-history.v1"
MAX_BYTES = 4 * 1024 * 1024
MAX_EVENTS = 4000
GENESIS = "0" * 64


def _history_path(review_path):
    path = Path(review_path).expanduser().resolve()
    return path.with_name(path.stem + ".history.jsonl")


def _digest(record):
    return hashlib.sha256(
        json.dumps(record, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def audit_review_history(review_path):
    path = _history_path(review_path)
    if not path.exists():
        return {"schema": SCHEMA, "valid": True, "events": 0, "last_digest": GENESIS,
                "file": str(path), "exists": False,
                "cryptographically_authenticated": False}
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("review history missing/oversized")
    previous = GENESIS
    n = 0
    last_review_sha = None
    with path.open("rb") as stream:
        for line in stream:
            n += 1
            if n > MAX_EVENTS or len(line) > 2048 or not line.endswith(b"\n"):
                raise ValueError("review history truncated or exceeds limits")
            try:
                row = json.loads(line)
            except (ValueError, UnicodeDecodeError) as e:
                raise ValueError("invalid review journal entry") from e
            if not isinstance(row, dict) or row.get("schema") != SCHEMA:
                raise ValueError("invalid review history schema")
            claimed = row.get("digest")
            core = {key: value for key, value in row.items() if key != "digest"}
            if row.get("previous") != previous or _digest(core) != claimed:
                raise ValueError("review history hash chain damaged")
            if not isinstance(row.get("review_sha256"), str):
                raise ValueError("invalid review snapshot hash")
            previous = claimed
            last_review_sha = row["review_sha256"]
    from .production_review import _hash
    review = Path(review_path).expanduser().resolve()
    if last_review_sha and _hash(review) != last_review_sha:
        raise ValueError("review file changed without journal event")
    return {"schema": SCHEMA, "valid": True, "events": n,
            "last_digest": previous, "file": str(path), "exists": True,
            "cryptographically_authenticated": False}


def append_review_history(review_path, action, details=None):
    if action not in ("review-mark", "review-refresh", "import-return"):
        raise ValueError("invalid review journal action")
    details = details or {}
    if not isinstance(details, dict):
        raise ValueError("history details must be object")
    prior = audit_review_history(review_path)
    if prior["events"] >= MAX_EVENTS:
        raise ValueError("review history too long; archive explicitly")
    from .production_review import _hash
    row = {
        "schema": SCHEMA,
        "previous": prior["last_digest"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "details": details,
        "review_sha256": _hash(review_path),
    }
    row["digest"] = _digest(row)
    encoded = (json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode()
    if len(encoded) > 2048:
        raise ValueError("review event exceeds 2 KiB")
    path = _history_path(review_path)
    if prior["events"] == 0 and not prior["exists"]:
        try:
            with path.open("xb") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException:
            # Don't remove a path that another writer could have created.
            raise
    else:
        with path.open("ab") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    return {"schema": SCHEMA, "events": prior["events"] + 1,
            "last_digest": row["digest"], "cryptographically_authenticated": False}
