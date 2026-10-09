"""Preflight and batch voice-pack creation for known model profiles.

Offline only: output packages are build artifacts, never device install
authorization. Every target must independently pass event mapping checks.
"""
import hashlib
import json
import shutil
from pathlib import Path

from .audio_qa import inspect_wav
from .catalog import event_by_id, event_by_semantic, event_profile_for_model, model_by_id
from .creator import MAX_AUDIO_BYTES, build_workspace, validate_workspace
from .models.registry import get as get_adapter

SCHEMA = "vvh.creator-preflight.v1"
BATCH_SCHEMA = "vvh.creator-batch.v1"
MAX_TARGETS = 16
MAX_EVENTS = 512


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(65536):
            digest.update(chunk)
    return digest.hexdigest()


def _input_files(root, manifest):
    rows = []
    if len(manifest["events"]) > MAX_EVENTS:
        raise ValueError("Creator project exceeds 512 audio event assignments")
    for semantic, rel in sorted(manifest["events"].items()):
        src = (root / rel).resolve()
        src.relative_to(root)
        size = src.stat().st_size
        if not 0 < size <= MAX_AUDIO_BYTES:
            raise ValueError(f"invalid audio file size for {semantic}")
        rows.append({
            "semantic": semantic, "file": rel, "bytes": size,
            "sha256": _sha256(src),
        })
    return rows


def preflight_workspace(path, model_id, *, check_audio=False):
    """Return exact numeric coverage, collisions and non-mutating readiness."""
    checked = validate_workspace(path)
    if not checked["ok"]:
        return {
            "schema": SCHEMA, "ready": False,
            "validation_errors": checked["errors"],
            "install_authorized": False,
        }
    root = Path(checked["workspace"]).resolve()
    manifest = checked["manifest"]
    target = model_by_id(model_id)
    profile = event_profile_for_model(target["id"])
    known = set(profile["known_event_ids"])
    core = set(profile.get("core_event_ids", [])) & known
    files = _input_files(root, manifest)
    producers = {}
    unassigned = []
    audio_warnings = []
    for row in files:
        semantic = row["semantic"]
        applicable = sorted({int(event["id"]) for event in event_by_semantic(semantic)
                             if int(event["id"]) in known})
        if not applicable:
            unassigned.append(semantic)
        for event_id in applicable:
            producers.setdefault(event_id, []).append(semantic)
        if check_audio and row["file"].lower().endswith(".wav"):
            try:
                quality = inspect_wav(root / row["file"])
                if quality["warnings"]:
                    audio_warnings.append({"semantic": semantic, "warnings": quality["warnings"]})
            except ValueError as exc:
                audio_warnings.append({"semantic": semantic, "warnings": ["invalid-wav"],
                                       "error": str(exc)})
    collisions = [
        {"event_id": event_id, "semantics": sorted(names)}
        for event_id, names in sorted(producers.items()) if len(names) > 1
    ]
    covered = set(producers)
    missing = sorted(known - covered)
    missing_core = sorted(core - covered)
    adapter = get_adapter(target["id"])
    package = target.get("package", {})
    warnings = list(checked["warnings"])
    if unassigned:
        warnings.append("some audio semantics do not map to this model")
    if missing_core:
        warnings.append("core model events remain unrecorded")
    if audio_warnings:
        warnings.append("audio signal QA warnings require human review")
    return {
        "schema": SCHEMA, "model_id": target["id"], "model_name": target["name"],
        "adapter": target["adapter"],
        "package_container": package.get("container"),
        "output_suffix": adapter.OUTPUT_SUFFIX,
        "known_event_count": len(known), "core_event_count": len(core),
        "mapped_event_ids": sorted(covered), "mapped_event_count": len(covered),
        "coverage_pct": round(len(covered)*100/len(known), 1) if known else 0.0,
        "missing_event_ids": missing, "missing_core_event_ids": missing_core,
        "missing_core_details": [{
            "id": event_id, "semantic": event_by_id(event_id)["semantic"],
            "description": event_by_id(event_id).get("description"),
        } for event_id in missing_core],
        "unmapped_semantics": unassigned,
        "collisions": collisions,
        "inputs": files,
        "audio_warnings": audio_warnings,
        "warnings": warnings,
        "validation_errors": [],
        "ready": len(covered) >= 5 and not collisions
                 and not any("invalid-wav" in row["warnings"] for row in audio_warnings),
        "install_authorized": False,
        "custom_install_verified_by_preflight": False,
        "note": "Build readiness is not vendor format, firmware or installation certification.",
    }


def batch_build_workspace(path, model_ids, output_dir, *, check_audio=False):
    """Build <=16 profiles, refuse existing output, and clean up on failure.

    The output directory is reserved via exclusive mkdir. A failure removes
    only the directory created by this invocation; no existing user files
    are replaced, and no device is accessed.
    """
    if isinstance(model_ids, str) or not isinstance(model_ids, (list, tuple)):
        raise ValueError("models must be a list of exact catalog IDs")
    if not 1 <= len(model_ids) <= MAX_TARGETS:
        raise ValueError("batch requires 1..16 target models")
    plans = [preflight_workspace(path, model, check_audio=check_audio) for model in model_ids]
    if not all(plan["ready"] for plan in plans):
        raise ValueError("batch preflight failed: " + "; ".join(
            f"{plan.get('model_id', 'invalid')} not ready"
            for plan in plans if not plan["ready"]
        ))
    canonicals = [plan["model_id"] for plan in plans]
    if len(set(canonicals)) != len(canonicals):
        raise ValueError("duplicate canonical model IDs in batch")
    workspace = Path(path).expanduser().resolve()
    out = Path(output_dir).expanduser().resolve()
    # Refuse output inside the workspace: it could expose intermediates to
    # other Creator operations or cause a recursive cleanup of user files.
    if out == workspace or workspace in out.parents:
        raise ValueError("batch output must be outside the Creator workspace")
    if out.exists() or out.is_symlink():
        raise FileExistsError(f"output directory already exists: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir(exist_ok=False)
    try:
        builds = []
        seen_output_names = set()
        for plan in plans:
            target_id = plan["model_id"]
            name = target_id.replace(".", "_") + plan["output_suffix"]
            if name.casefold() in seen_output_names:
                raise ValueError("duplicate output filenames")
            seen_output_names.add(name.casefold())
            dest = out / name
            artifact = build_workspace(workspace, target_id, dest)
            if not dest.is_file() or dest.stat().st_size == 0:
                raise RuntimeError(f"missing package output for {target_id}")
            # Source audio can change while encoding. Refuse to publish a
            # mixed-version batch and preserve only user's original inputs.
            actual = _input_files(workspace, validate_workspace(workspace)["manifest"])
            if actual != plan["inputs"]:
                raise RuntimeError("Creator audio changed during batch build")
            builds.append({
                "model_id": target_id, "file": name,
                "bytes": dest.stat().st_size, "sha256": _sha256(dest),
                "events": artifact["events"], "coverage_pct": plan["coverage_pct"],
                "output_suffix": plan["output_suffix"], "install_authorized": False,
                "manufacturer_format_verified": False,
            })
        manifest = {
            "schema": BATCH_SCHEMA, "source_pack_id": validate_workspace(workspace)["manifest"]["id"],
            "model_count": len(builds), "models": canonicals,
            "packages": builds, "install_authorized": False,
            "license_review_required": True,
            "note": "Offline packages only; review rights and exact-device acceptance before any installation.",
        }
        (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False,
                                                        sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return {"output": str(out), **manifest}
    except BaseException:
        shutil.rmtree(out)
        raise
