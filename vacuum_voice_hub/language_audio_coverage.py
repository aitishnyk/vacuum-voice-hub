"""Compare translated TEXT with audio actually assigned in a Creator workspace.

Text templates and audio file existence are different sources of truth.
Neither determines that a speaker really speaks the declared language.
"""
from .catalog import event_profile_for_model, model_by_id
from .creator import validate_workspace
from .script_packs import script_for_model

SCHEMA = "vvh.language-audio-coverage.v1"


def language_audio_coverage(workspace, locale, model_id, *, overlay_path=None):
    validation = validate_workspace(workspace)
    if not validation["ok"]:
        return {"schema": SCHEMA, "ok": False,
                "validation_errors": validation["errors"],
                "install_authorized": False}
    script = script_for_model(locale, model_id, overlay_path)
    model = model_by_id(model_id)
    profile = event_profile_for_model(model["id"])
    allowed = set(profile["known_event_ids"])
    workspace_language = validation["manifest"]["language"]
    language_match = workspace_language.casefold() == locale.casefold()
    recorded = set(validation["manifest"]["events"])
    translated = {row["semantic"] for row in script["entries"] if row["mapped_to_model"]}
    rows = []
    text_ids = set()
    audio_ids = set()
    both_ids = set()
    for row in script["entries"]:
        ids = set(row["target_event_ids"])
        text_ids |= ids
        exists = row["semantic"] in recorded
        if exists:
            audio_ids |= ids
        if exists and language_match:
            both_ids |= ids
        rows.append({
            "semantic": row["semantic"],
            "target_event_ids": sorted(ids),
            "text_ready": True,
            "audio_assigned": exists,
            "audio_declared_in_requested_locale": exists and language_match,
            "translation_source": row["translation_source"],
        })
    recorded_without_text = sorted(recorded - translated)
    return {
        "schema": SCHEMA, "ok": True, "locale": locale,
        "model_id": model["id"], "model_event_count": len(allowed),
        "workspace_language": workspace_language,
        "workspace_language_matches_script": language_match,
        "scripted_event_count": len(translated),
        "audio_assigned_in_script": sum(row["audio_assigned"] for row in rows),
        "text_model_event_count": len(text_ids),
        "audio_assigned_model_event_count": len(audio_ids),
        "declared_locale_text_and_audio_event_count": len(both_ids),
        "text_coverage_pct": round(len(text_ids) * 100 / len(allowed), 1) if allowed else 0,
        "audio_coverage_pct": round(len(both_ids) * 100 / len(allowed), 1) if allowed else 0,
        "recorded_semantics_without_supplied_translation": recorded_without_text,
        "missing_audio_semantics": sorted(translated - recorded),
        "overlay_count": script["overlay_count"],
        "rows": rows,
        "speaker_language_verified": False,
        "recording_license_verified": False,
        "installation_hardware_verified_by_report": False,
        "install_authorized": False,
        "note": "Assigned audio is file presence only, not verified pronunciation, recording quality or firmware compatibility.",
    }
