"""Fail-closed, offline candidate voice-package research workflow.

A candidate assessment is not an installer, format certification or proof of
physical compatibility. Neither evidence reports nor archive contents can
change the model registry or authorize a transport.
"""
import hashlib
import re
from pathlib import Path

from .archive_inspector import (
    ArchiveInspectionError, MAX_ARCHIVE_BYTES, inspect_archive
)
from .catalog import event_profile_for_model, model_by_id
from .transport_evidence import EvidenceError, inspect_file

SCHEMA = "vvh.research-assessment.v1"
_NUMERIC_OGG = re.compile(r"(?:[0-9]+)\.ogg\Z", re.IGNORECASE)
_IJAI_MP3 = re.compile(r"sound_[A-Za-z0-9_-]+\.mp3\Z", re.IGNORECASE)
_ROBOROCK_WAV = {
    "start.wav", "pause.wav", "finish.wav", "home.wav", "charging.wav",
}


class ResearchError(ValueError):
    """Candidate input or evidence mismatch."""


def _archive_sha256(path):
    total = 0
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(65536):
            total += len(block)
            if total > MAX_ARCHIVE_BYTES:
                raise ResearchError("candidate exceeds 128 MiB")
            digest.update(block)
    if not total:
        raise ResearchError("empty candidate")
    return digest.hexdigest(), total


def _classify(inventory, known_ids):
    audio = [row for row in inventory["files"] if row["audio"]]
    numeric = set()
    ijai = 0
    robo = 0
    for row in audio:
        basename = row["path"].rsplit("/", 1)[-1]
        if _NUMERIC_OGG.fullmatch(basename):
            numeric.add(int(basename[:-4]))
        if _IJAI_MP3.fullmatch(basename):
            ijai += 1
        if basename.lower() in _ROBOROCK_WAV:
            robo += 1
    candidates = [
        name for name, count in (
            ("dreame-numeric-ogg-candidate", len(numeric)),
            ("ijai-named-mp3-candidate", ijai),
            ("roborock-named-wav-candidate", robo),
        ) if count >= 5
    ]
    layout = candidates[0] if len(candidates) == 1 else (
        "mixed-ambiguous" if candidates else "unidentified"
    )
    return {
        "candidate_layout": layout,
        "matched_profile_numeric_ids": len(numeric & known_ids),
        "outside_profile_numeric_ids": sorted(numeric - known_ids),
        "observed_numeric_ids": len(numeric),
        "audio_files": len(audio),
        "note": "Layout detection is a filename heuristic; it never proves a vendor format or install compatibility.",
    }


def assess_candidate(path, model_id, evidence_path=None):
    """Inspect locally, verify optional declared hash and return research-only JSON data."""
    model = model_by_id(model_id)
    canonical = model["id"]
    archive = Path(path).expanduser()
    if not archive.is_file():
        raise ResearchError("candidate file not found")
    digest, size = _archive_sha256(archive)
    suffix = archive.suffix.lower()
    opaque = False
    try:
        inventory = inspect_archive(archive)
    except ArchiveInspectionError as exc:
        # Proprietary encrypted .pkg cannot safely be inspected as an archive.
        # Retain only its hash and size and never treat it as installable.
        if suffix != ".pkg":
            raise ResearchError(str(exc)) from exc
        opaque = True
        inventory = None

    evidence = None
    if evidence_path is not None:
        try:
            evidence = inspect_file(evidence_path, expected_model=canonical)
        except (EvidenceError, OSError) as exc:
            raise ResearchError(f"invalid research evidence: {exc}") from exc
        if evidence["package_sha256"] != digest:
            raise ResearchError("evidence SHA-256 does not match candidate bytes")
        # The original report also declares exact byte size and format.
        from .transport_evidence import MAX_BYTES
        import json
        raw_path = Path(evidence_path)
        with raw_path.open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ResearchError("evidence file exceeds 64 KiB")
        record = json.loads(raw.decode("utf-8"))
        if record["package"]["size_bytes"] != size:
            raise ResearchError("evidence size does not match candidate bytes")
        fmt = record["package"]["format"]
        if fmt == "zip" and (opaque or inventory["container"] != "zip"):
            raise ResearchError("evidence format disagrees with candidate")
        if fmt == "tar.gz":
            with archive.open("rb") as stream:
                magic = stream.read(2)
            if opaque or inventory["container"] != "tar" or magic != b"\x1f\x8b":
                raise ResearchError("evidence tar.gz format disagrees with candidate")
        if fmt in {"pkg", "ogg", "mp3"}:
            if not opaque or fmt != "pkg":
                raise ResearchError("opaque format is unsupported by archive inspector")
    known_ids = set(event_profile_for_model(canonical)["known_event_ids"])
    findings = (
        {"candidate_layout": "opaque-proprietary-package", "matched_profile_numeric_ids": 0,
         "outside_profile_numeric_ids": [], "observed_numeric_ids": 0, "audio_files": 0,
         "note": "Opaque bytes were not decrypted or parsed."}
        if opaque else _classify(inventory, known_ids)
    )
    return {
        "schema": SCHEMA,
        "model_id": canonical,
        "model_adapter": model["adapter"],
        "model_install_policy": (model.get("transport") or {}).get("verification", "unknown"),
        "candidate_sha256": digest,
        "candidate_size_bytes": size,
        "inspection": "opaque" if opaque else "archive",
        "inventory": inventory,
        "findings": findings,
        "evidence_assessment": evidence,
        "evidence_matched": evidence is not None,
        "hardware_verified_by_assessment": False,
        "install_authorized": False,
        "registry_mutated": False,
    }
