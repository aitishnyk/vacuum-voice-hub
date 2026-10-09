"""Safe offline import of human-returned reviews; no ZIP extraction.

Even an approved remote review is an *untrusted assertion*. Import stores it
as an external claim and resets all local decisions to draft.
"""
import hashlib
import json
import stat
import zipfile
from pathlib import Path

from .production_review import (
    SCHEMA, MAX_REVIEW_BYTES, MAX_BUNDLE_BYTES, MAX_ROWS,
    STATUSES, _load_json, _hash, _snapshot, _audio_snapshot,
    create_review, _write_review, _reviewer,
)

MAX_ZIP_BYTES = 105 * 1024 * 1024
MAX_ZIP_ENTRIES = MAX_ROWS + 2
MAX_JSON_READ = MAX_REVIEW_BYTES


def _json_bytes(payload):
    if not 0 < len(payload) <= MAX_JSON_READ:
        raise ValueError("returned review JSON exceeds 512 KiB")
    def no_duplicates(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("duplicate JSON field in returned review")
            obj[key] = value
        return obj
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=no_duplicates)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid UTF-8 review JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("returned review must be a JSON object")
    return value


def _bundle_payload(path):
    """Read exact allowlisted ZIP members in-memory, never writing extracted files."""
    src = Path(path)
    if not src.is_file() or not 0 < src.stat().st_size <= MAX_ZIP_BYTES:
        raise ValueError("returned review bundle exceeds 105 MiB or is absent")
    if not zipfile.is_zipfile(src):
        raise ValueError("invalid returned review ZIP")
    with zipfile.ZipFile(src) as archive:
        members = archive.infolist()
        names = [entry.filename for entry in members]
        if not 2 <= len(members) <= MAX_ZIP_ENTRIES:
            raise ValueError("unexpected number of bundle members")
        if len(names) != len(set(names)):
            raise ValueError("duplicate ZIP paths")
        if "review.json" not in names or "audit.json" not in names:
            raise ValueError("review ZIP requires review.json and audit.json")
        total = 0
        for info in members:
            name = info.filename
            if name not in {"review.json", "audit.json"} and not name.startswith("audio/audio/"):
                raise ValueError("unexpected review ZIP path")
            if name.startswith("/") or "\\" in name or ".." in Path(name).parts or name.endswith("/"):
                raise ValueError("unsafe review ZIP member")
            if info.flag_bits & 0x1 or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("encrypted or symlink ZIP entry")
            max_size = MAX_REVIEW_BYTES if name.endswith(".json") else 25 * 1024 * 1024
            if info.file_size > max_size:
                raise ValueError("review ZIP member too large")
            total += info.file_size
            if total > MAX_BUNDLE_BYTES + MAX_REVIEW_BYTES * 2:
                raise ValueError("review ZIP inflated contents too large")
        record = _json_bytes(archive.read("review.json"))
        audit = _json_bytes(archive.read("audit.json"))
        if not isinstance(audit, dict) or audit.get("schema") != SCHEMA:
            raise ValueError("invalid included review audit")
        return record, {x: archive.read(x) for x in names if x.startswith("audio/audio/")}


def _returned(path):
    source = Path(path).expanduser().resolve(strict=True)
    if not source.is_file():
        raise ValueError("returned review must be a file")
    if source.suffix.lower() == ".json":
        if source.stat().st_size > MAX_REVIEW_BYTES:
            raise ValueError("returned review too large")
        return _json_bytes(source.read_bytes()), {}, _hash(source)
    if source.suffix.lower() == ".zip":
        review, audio = _bundle_payload(source)
        return review, audio, _hash(source)
    raise ValueError("returned review must be .json or .zip")


def import_review(source, workspace, output, *, overlay_path=None,
                  expected_model=None, expected_locale=None):
    """Bind returned review to selected *local* workspace, without touching its audio."""
    candidate, embedded_audio, source_sha = _returned(source)
    if candidate.get("schema") != SCHEMA:
        raise ValueError("unsupported returned review schema")
    for k in ("model_id", "locale", "pack_id"):
        if not isinstance(candidate.get(k), str):
            raise ValueError("returned review identity incomplete")
    if expected_model and candidate["model_id"] != expected_model:
        raise ValueError("returned model ID differs from selected target")
    if expected_locale and candidate["locale"] != expected_locale:
        raise ValueError("returned locale differs from selected language")
    root, manifest, target, script, fresh = _snapshot(
        workspace, candidate["locale"], candidate["model_id"], overlay_path)
    if candidate["pack_id"] != manifest["id"]:
        raise ValueError("returned pack ID does not match local Creator project")
    if candidate.get("workspace_manifest_sha256") != _hash(root / "manifest.json"):
        raise ValueError("returned Creator manifest digest mismatch")
    digest = hashlib.sha256(json.dumps(
        [(r["semantic"], r["event_ids"], r["text"]) for r in fresh],
        ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if candidate.get("text_script_digest") != digest:
        raise ValueError("returned text/profile digest mismatch")
    if candidate.get("overlay_required_for_audit") and overlay_path is None:
        raise ValueError("original translation overlay required to import")
    tasks = candidate.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != len(fresh):
        raise ValueError("returned task count differs from local model")
    claims = {}
    used_audio = set()
    for incoming, local in zip(tasks, fresh):
        if not isinstance(incoming, dict) or any(
            incoming.get(k) != local[k] for k in ("semantic", "event_ids", "text", "audio")
        ):
            raise ValueError("returned review task identity or recording digest mismatch")
        state = incoming.get("review")
        if not isinstance(state, dict) or state.get("status") not in STATUSES:
            raise ValueError("invalid returned review status")
        if state["status"] != "draft" and not local["audio"]:
            raise ValueError("remote reviewer marked a missing recording")
        reviewer = state.get("reviewer")
        if reviewer is not None and not _reviewer(reviewer):
            raise ValueError("invalid returned reviewer identity")
        note = state.get("note")
        if note is not None and (not isinstance(note, str) or len(note) > 500):
            raise ValueError("review note too long")
        if state["status"] in ("listened", "approved") and not _reviewer(reviewer):
            raise ValueError("remote listening/approval lacks reviewer")
        if state["status"] == "approved" and not (
            state.get("language_attested") is True and state.get("rights_attested") is True
        ):
            raise ValueError("remote approval lacks two explicit attestations")
        local["external_review_claim"] = {
            "status": state["status"], "reviewer": reviewer,
            "note": note, "reviewed_at": state.get("reviewed_at"),
            "language_attested": state.get("language_attested") is True,
            "rights_attested": state.get("rights_attested") is True,
            "trusted": False,
        }
        claims[state["status"]] = claims.get(state["status"], 0) + 1
        if local["audio"]:
            name = "audio/" + local["audio"]["file"]
            if name in embedded_audio:
                if hashlib.sha256(embedded_audio[name]).hexdigest() != local["audio"]["sha256"]:
                    raise ValueError("audio inside returned ZIP differs from local source")
                used_audio.add(name)
    if set(embedded_audio) != used_audio:
        raise ValueError("returned ZIP has unassigned or duplicate source audio")
    # Only after every source, text, model, digest and ZIP member validates:
    dest = Path(output).expanduser().absolute()
    result = create_review(root, candidate["locale"], target["id"], dest,
                           overlay_path=overlay_path)
    try:
        record = _load_json(dest)
        for row, clean in zip(record["tasks"], fresh):
            row["external_review_claim"] = clean["external_review_claim"]
            # Intentionally keep local approvals at draft after import.
            assert row["review"]["status"] == "draft"
        record["import_provenance"] = {
            "schema": "vvh.returned-review.v1",
            "source_sha256": source_sha, "untrusted_human_claims": True,
            "no_local_approval_transferred": True,
        }
        _write_review(dest, record)
        from .review_history import append_review_history
        append_review_history(dest, "import-return", {
            "source_sha256": source_sha,
            "reviewer_claims": claims,
            "local_approvals_transferred": 0,
        })
        return {
            "schema": "vvh.returned-review.v1", "file": str(dest),
            "model_id": target["id"], "locale": candidate["locale"],
            "source_sha256": source_sha, "claims": claims,
            "local_approvals_transferred": 0,
            "embedded_audio_checked": len(used_audio),
            "original_audio_modified": False,
            "install_authorized": False,
        }
    except BaseException:
        dest.unlink(missing_ok=True)
        raise
