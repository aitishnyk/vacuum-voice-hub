"""Integrated read-only Universal Voice Studio inspection API.

Synthesizes existing real Creator, catalog, language, review and adapter
engines. Does not automatically attest rights, voices or device installation.
"""
import hashlib
import json
from pathlib import Path

from .catalog import model_by_id, models, voices
from .creator import validate_workspace
from .creator_batch import preflight_workspace
from .language_audio_coverage import language_audio_coverage
from .script_packs import list_locales, script_for_model
from .voice_library import _pack

SCHEMA = "vvh.universal-studio.v1"
MAX_OUTPUT = 256 * 1024


def studio_capabilities():
    model_rows = models()
    voices_rows = voices()
    locales = list_locales()
    return {
        "schema": "vvh.universal-studio-capabilities.v1",
        "model_profiles": len(model_rows),
        "recorded_voice_variants": len(voices_rows),
        "text_script_locales": len(locales),
        "physically_verified_models": sum(bool(r.get("device_tested")) for r in model_rows),
        "features": [
            "creator-workspaces", "audio-qa", "master-batch", "audio-ab",
            "timeline", "language-review", "pronunciation-lexicon",
            "community-evidence-moderation", "adapter-interchange",
            "attributed-voice-library", "creator-backup-and-recovery",
        ],
        "model_profiles_are_physical_installs": False,
        "text_locales_are_recordings": False,
        "community_claims_are_independent_verification": False,
        "hardware_install_authorized": False,
    }


def inspect_studio(workspace, model_id, locale, *, overlay_path=None,
                   adapter_path=None, translation_review=None,
                   recording_review=None, check_audio=False):
    """Compose current audited engines without modifying source files."""
    if type(check_audio) is not bool:
        raise ValueError("check_audio must be true or false")
    model = model_by_id(model_id)
    canonical_id = model["id"]
    script = script_for_model(locale, canonical_id, overlay_path)
    validation = validate_workspace(workspace)
    result = {
        "schema": SCHEMA, "model_id": canonical_id,
        "model_name": model["name"], "used_model_alias": model_id != canonical_id,
        "locale": locale, "locale_script_count": script["scripted_count"],
        "text_is_not_recorded_audio": True,
        "workspace_valid": bool(validation["ok"]),
        "workspace_errors": list(validation["errors"]),
        "offline_pack_build_ready": False,
        "hardware_tested_in_catalog": bool(model.get("device_tested")),
        "independent_human_language_verified": False,
        "redistribution_rights_verified": False,
        "hardware_install_authorized": False,
        "creator_source_mutated": False,
        "remote_operations_performed": False,
    }
    if not validation["ok"]:
        result["note"] = "Creator workspace validation failed; remaining model/audio gates skipped."
        return result
    report = preflight_workspace(workspace, canonical_id,
                                 check_audio=check_audio)
    coverage = language_audio_coverage(workspace, locale, canonical_id,
                                       overlay_path=overlay_path)
    pack = _pack(workspace)
    result.update({
        "pack_id": pack["pack_id"],
        "declared_license": pack["license_declared"],
        "source_manifest_sha256": pack["manifest_sha256"],
        "source_audio_sha256": pack["audio_fingerprint_sha256"],
        "assigned_audio_semantics": pack["events"],
        "model_known_events": report["known_event_count"],
        "model_mapped_events": report["mapped_event_count"],
        "missing_core_event_ids": report["missing_core_event_ids"],
        "unmapped_semantics": report["unmapped_semantics"],
        "mapping_collisions": report["collisions"],
        "preflight_warnings": report["warnings"],
        "workspace_language_matches_script": coverage["workspace_language_matches_script"],
        "scripted_semantics_missing_audio": coverage["missing_audio_semantics"],
        "translation_overlay_count": script["overlay_count"],
        "offline_pack_build_ready": bool(report["ready"]),
    })
    if check_audio:
        result["audio_qa_warnings"] = report["audio_warnings"]
    if adapter_path is not None:
        from .adapter_interchange import adapter_preflight
        adapter = adapter_preflight(workspace, adapter_path)
        if adapter["model_id"] != canonical_id:
            raise ValueError("adapter descriptor model does not match studio target")
        result["adapter"] = {
            "adapter_id": adapter["adapter_id"],
            "source_sha256": adapter["descriptor_sha256"],
            "mapped_events": len(adapter["entries"]),
            "ready_for_offline_interchange": True,
            "hardware_install_authorized": False,
        }
    if translation_review is not None:
        from .language_review import audit_language_review
        record = audit_language_review(translation_review,
                                       overlay_path=overlay_path)
        if record["model_id"] != canonical_id or record["locale"] != locale:
            raise ValueError("translation review model/locale mismatch")
        result["translation_review"] = {
            "claimed_human_approvals": record["human_approval_claims"],
            "counts": record["counts"], "snapshot_current": True,
            "independently_verified": False,
        }
    if recording_review is not None:
        from .production_review import audit_review
        reviewed = audit_review(recording_review, workspace=workspace,
                                overlay_path=overlay_path)
        if reviewed["model_id"] != canonical_id or reviewed["locale"] != locale:
            raise ValueError("recording review model/locale mismatch")
        result["recording_review"] = {
            "recorded_tasks": reviewed["audio_present"],
            "approved_with_matching_audio": reviewed["approved_with_matching_audio"],
            "valid": reviewed["valid"], "issues": reviewed["issues"],
            "independently_verified": False,
        }
    return result


def export_studio_report(workspace, model_id, locale, output, **options):
    report = inspect_studio(workspace, model_id, locale, **options)
    dest = Path(output).expanduser().absolute()
    if dest.suffix.lower() != ".json" or dest.is_symlink() or dest.exists():
        raise FileExistsError("studio report output must be a new JSON file")
    data = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    if len(data) > MAX_OUTPUT:
        raise ValueError("Studio report exceeds 256 KiB")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("xb") as stream:
        try:
            stream.write(data)
        except BaseException:
            stream.close()
            dest.unlink(missing_ok=True)
            raise
    return {"schema": SCHEMA, "output": str(dest),
            "report_sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "hardware_install_authorized": False,
            "redistribution_rights_verified": False}
