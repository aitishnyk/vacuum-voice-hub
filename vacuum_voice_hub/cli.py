import argparse,getpass,json
from .catalog import voices,models,voice_by_id,backlog,model_by_id,categories,events,event_profile_for_model
from .build import build_voice
from .install import install_voice
from .server import serve
from .stock import list_stock,install_stock
from .preview import preview_file
from .local_import import convert_local
from .creator import (
    new_workspace,validate_workspace,assign_audio,remove_event,
    workspace_model_coverage,build_workspace,list_workspaces
)
from .history import load_history
from .report import build_report,write_report,validate_report
from .sitegen import build_site,verify_site
from .release import build_release,verify_release
from . import credentials,miot,__version__

def _dump(x):
    print(json.dumps(x,ensure_ascii=False,indent=2,default=str))

def _resolve_token(a):
    direct=getattr(a,"token",None)
    credential=getattr(a,"credential",None)
    if direct and credential:
        raise SystemExit("Use either --token or --credential, not both")
    if credential:
        return credentials.load(credential)
    if direct:
        return direct
    return getpass.getpass("TOKEN (32 hex, hidden): ").strip()

def _add_auth_args(s):
    s.add_argument("--token")
    s.add_argument("--credential",help="Read token from OS Keychain/Secret Service")

def _parse_category_fallbacks(values):
    out={};valid=set(categories())
    for raw in values or []:
        if "=" not in raw:
            raise SystemExit(f"--fallback-category expects CATEGORY=VOICE, got {raw!r}")
        category,voice_id=raw.split("=",1)
        category=category.strip();voice_id=voice_id.strip()
        if category not in valid:
            raise SystemExit(f"Unknown category {category!r}. Valid: {', '.join(sorted(valid))}")
        if not voice_id:
            raise SystemExit(f"Missing voice id for fallback category {category}")
        out[category]=voice_id
    return out

def _add_build_args(s):
    s.add_argument("voice_id")
    s.add_argument("--model",default="dreame.vacuum.r2209")
    s.add_argument("--fallback",help="Default fallback voice for all remaining missing events")
    s.add_argument("--fallback-category",action="append",default=[],metavar="CATEGORY=VOICE",help="Fill only one semantic category; repeatable")

def _creator_parser(sub):
    c=sub.add_parser("creator",help="Create and build semantic vvh.voicepack.v1 packs")
    cs=c.add_subparsers(dest="creator_cmd",required=True)
    s=cs.add_parser("new");s.add_argument("path",nargs="?");s.add_argument("--id",required=True,dest="pack_id");s.add_argument("--name",required=True);s.add_argument("--author",required=True);s.add_argument("--language",required=True);s.add_argument("--adult",action="store_true");s.add_argument("--license",default="UNLICENSED",dest="license_name");s.add_argument("--source-url");s.add_argument("--description")
    cs.add_parser("list")
    s=cs.add_parser("validate");s.add_argument("path")
    s=cs.add_parser("assign");s.add_argument("path");s.add_argument("semantic");s.add_argument("audio_file")
    s=cs.add_parser("remove");s.add_argument("path");s.add_argument("semantic")
    s=cs.add_parser("coverage");s.add_argument("path");s.add_argument("--model",default="dreame.vacuum.r2209")
    s=cs.add_parser("qa",help="Read-only audio quality audit; never installs");s.add_argument("path");s.add_argument("--model");s.add_argument("--decode-compressed",action="store_true",help="Opt-in bounded local FFmpeg decoding")
    s=cs.add_parser("build");s.add_argument("path");s.add_argument("--model",default="dreame.vacuum.r2209");s.add_argument("--output")
    s=cs.add_parser("preflight",help="Read-only model event mapping and collision report")
    s.add_argument("path")
    s.add_argument("--model",default="dreame.vacuum.r2209")
    s.add_argument("--check-audio",action="store_true",help="Check audio signal quality")
    s.add_argument("--decode-compressed",action="store_true",help="Opt-in local FFmpeg analysis of non-WAV sources")
    s=cs.add_parser("batch",help="Build offline output packages for 1..16 chosen model IDs")
    s.add_argument("path")
    s.add_argument("--model",action="append",required=True,help="Repeat once per target device")
    s.add_argument("--output-dir",required=True,help="New directory; refuses existing paths")
    s.add_argument("--check-audio",action="store_true")
    s.add_argument("--decode-compressed",action="store_true")

    s=cs.add_parser("language-coverage",help="Compare translated text and local audio per model")
    s.add_argument("path")
    s.add_argument("--language",required=True)
    s.add_argument("--model",default="dreame.vacuum.r2209")
    s.add_argument("--overlay",help="Local text translation overlay")
    s=cs.add_parser("gain-preview",help="Create separate gain-adjusted WAV; never overwrite")
    s.add_argument("audio_file")
    s.add_argument("--gain-db",type=float,required=True)
    s.add_argument("--output",required=True)
    s=cs.add_parser("master-preview",help="Non-destructive offline silence trim, peak normalization and fades")
    s.add_argument("audio_file")
    s.add_argument("--output",required=True,help="New WAV preview path, never overwrites")
    s.add_argument("--target-peak-dbfs",type=float,default=-3.0)
    s.add_argument("--silence-dbfs",type=float,default=-45.0)
    s.add_argument("--padding-ms",type=float,default=80.0)
    s.add_argument("--fade-ms",type=float,default=8.0)
    s.add_argument("--no-trim-silence",action="store_true")
    s=cs.add_parser("master-batch",help="Non-destructive offline batch mastering")
    s.add_argument("--input-dir",required=True)
    s.add_argument("--output-dir",required=True)
    s.add_argument("--max-files",type=int,default=64)
    s.add_argument("--target-peak-dbfs",type=float,default=-3.0)
    s.add_argument("--silence-dbfs",type=float,default=-45.0)
    s.add_argument("--padding-ms",type=float,default=80.0)
    s.add_argument("--fade-ms",type=float,default=8.0)
    s.add_argument("--no-trim-silence",action="store_true")
    s=cs.add_parser("audio-compare",help="Read-only two-clip signal A/B QA")
    s.add_argument("first")
    s.add_argument("second")
    review=cs.add_parser("review",help="Local human recording checklist and QA sign-off")
    rs=review.add_subparsers(dest="review_cmd",required=True)
    s=rs.add_parser("init",help="New recording assignment checklist; refuses overwrite")
    s.add_argument("workspace")
    s.add_argument("--language",required=True)
    s.add_argument("--model",default="dreame.vacuum.r2209")
    s.add_argument("--overlay")
    s.add_argument("--output",required=True)
    s=rs.add_parser("audit",help="Verify review and hashes against current recordings")
    s.add_argument("path")
    s.add_argument("--workspace")
    s.add_argument("--overlay")
    s=rs.add_parser("refresh",help="Refresh recordings; reset changed tasks without losing unchanged reviews")
    s.add_argument("path")
    s.add_argument("--overlay")
    s=rs.add_parser("mark",help="Advance draft -> recorded -> listened -> approved")
    s.add_argument("path")
    s.add_argument("--semantic",required=True)
    s.add_argument("--status",required=True,choices=["draft","recorded","listened","approved"])
    s.add_argument("--reviewer")
    s.add_argument("--note")
    s.add_argument("--language-attested",action="store_true")
    s.add_argument("--rights-attested",action="store_true")
    s.add_argument("--overlay")
    s=rs.add_parser("import",help="Safely bind a returned JSON or review ZIP to a chosen local project")
    s.add_argument("returned_file")
    s.add_argument("--workspace",required=True)
    s.add_argument("--output",required=True,help="New review JSON; original review and audio remain unchanged")
    s.add_argument("--model",help="Required model identity expected from collaborator")
    s.add_argument("--language",help="Required locale expected from collaborator")
    s.add_argument("--overlay",help="Exact original local translation overlay if applicable")
    s=rs.add_parser("history",help="Audit local hash-linked reviewer decision history")
    s.add_argument("path")
    s=rs.add_parser("attest",help="Sign approved human review with external Ed25519 PEM key")
    s.add_argument("path")
    s.add_argument("--semantic",required=True)
    s.add_argument("--private-key",required=True)
    s.add_argument("--output",required=True)
    s.add_argument("--overlay")
    s=rs.add_parser("verify-attestation",help="Check detached signature and current source audio")
    s.add_argument("attestation_file")
    s.add_argument("--public-key",required=True)
    s.add_argument("--review",required=True)
    s.add_argument("--overlay")
    s=rs.add_parser("audio-acceptance",help="Compare per-clip audio QA with human review")
    s.add_argument("path")
    s.add_argument("--max-clips",type=int,default=16)
    s.add_argument("--decode-compressed",action="store_true")
    s.add_argument("--overlay")
    s=rs.add_parser("sign-pack",help="Sign all Creator review audio assignments with user Ed25519 key")
    s.add_argument("path")
    s.add_argument("--private-key",required=True)
    s.add_argument("--output",required=True)
    s.add_argument("--require-approved",action="store_true")
    s.add_argument("--overlay")
    s=rs.add_parser("verify-pack",help="Verify whole-pack Ed25519 and every current local audio hash")
    s.add_argument("signed_file")
    s.add_argument("--public-key",required=True)
    s.add_argument("--review",required=True)
    s.add_argument("--overlay")
    s=rs.add_parser("bundle",help="New reviewer ZIP; audio inclusion requires explicit opt-in")
    s.add_argument("path")
    s.add_argument("--output",required=True)
    s.add_argument("--include-audio",action="store_true")
    s.add_argument("--overlay")
    s=cs.add_parser("events");s.add_argument("--model");s.add_argument("--category")

def _creator_main(a):
    if a.creator_cmd=="new":
        _dump(new_workspace(a.path,pack_id=a.pack_id,name=a.name,author=a.author,language=a.language,adult=a.adult,license_name=a.license_name,source_url=a.source_url,description=a.description))
    elif a.creator_cmd=="list":_dump(list_workspaces())
    elif a.creator_cmd=="validate":_dump(validate_workspace(a.path))
    elif a.creator_cmd=="assign":_dump(assign_audio(a.path,a.semantic,a.audio_file))
    elif a.creator_cmd=="remove":_dump(remove_event(a.path,a.semantic))
    elif a.creator_cmd=="coverage":_dump(workspace_model_coverage(a.path,a.model))
    elif a.creator_cmd=="qa":
        from .audio_qa import inspect_workspace
        _dump(inspect_workspace(a.path,a.model,decode_compressed=a.decode_compressed))
    elif a.creator_cmd=="build":_dump(build_workspace(a.path,a.model,a.output))
    elif a.creator_cmd=="preflight":
        from .creator_batch import preflight_workspace
        _dump(preflight_workspace(a.path,a.model,check_audio=a.check_audio,decode_compressed=a.decode_compressed))
    elif a.creator_cmd=="batch":
        from .creator_batch import batch_build_workspace
        _dump(batch_build_workspace(a.path,a.model,a.output_dir,check_audio=a.check_audio,decode_compressed=a.decode_compressed))

    elif a.creator_cmd=="language-coverage":
        from .language_audio_coverage import language_audio_coverage
        _dump(language_audio_coverage(a.path,a.language,a.model,overlay_path=a.overlay))
    elif a.creator_cmd=="gain-preview":
        from .audio_advanced import preview_gain
        _dump(preview_gain(a.audio_file,a.output,a.gain_db))
    elif a.creator_cmd=="master-preview":
        from .audio_mastering import master_preview
        _dump(master_preview(a.audio_file,a.output,target_peak_dbfs=a.target_peak_dbfs,
                             silence_dbfs=a.silence_dbfs,padding_ms=a.padding_ms,
                             fade_ms=a.fade_ms,trim_silence=not a.no_trim_silence))
    elif a.creator_cmd=="master-batch":
        from .audio_batch import master_batch
        _dump(master_batch(a.input_dir,a.output_dir,max_files=a.max_files,
                           target_peak_dbfs=a.target_peak_dbfs,
                           silence_dbfs=a.silence_dbfs,padding_ms=a.padding_ms,
                           fade_ms=a.fade_ms,trim_silence=not a.no_trim_silence))
    elif a.creator_cmd=="audio-compare":
        from .audio_compare import compare_audio
        _dump(compare_audio(a.first,a.second))
    elif a.creator_cmd=="review":
        from .production_review import (create_review, audit_review, mark_review,
                                        refresh_review, export_review_bundle)
        if a.review_cmd=="init":
            _dump(create_review(a.workspace,a.language,a.model,a.output,overlay_path=a.overlay))
        elif a.review_cmd=="audit":
            _dump(audit_review(a.path,workspace=a.workspace,overlay_path=a.overlay))
        elif a.review_cmd=="refresh":
            _dump(refresh_review(a.path,overlay_path=a.overlay))
        elif a.review_cmd=="mark":
            _dump(mark_review(a.path,a.semantic,a.status,reviewer=a.reviewer,note=a.note,
                              language_attested=a.language_attested,
                              rights_attested=a.rights_attested,overlay_path=a.overlay))
        elif a.review_cmd=="import":
            from .review_handoff import import_review
            _dump(import_review(a.returned_file,a.workspace,a.output,
                                overlay_path=a.overlay,expected_model=a.model,
                                expected_locale=a.language))
        elif a.review_cmd=="history":
            from .review_history import audit_review_history
            _dump(audit_review_history(a.path))
        elif a.review_cmd=="attest":
            from .reviewer_attestation import sign_review
            _dump(sign_review(a.path,a.semantic,a.private_key,a.output,overlay_path=a.overlay))
        elif a.review_cmd=="verify-attestation":
            from .reviewer_attestation import verify_attestation
            _dump(verify_attestation(a.attestation_file,a.public_key,a.review,
                                      overlay_path=a.overlay))
        elif a.review_cmd=="audio-acceptance":
            from .review_audio_acceptance import inspect_review_audio
            _dump(inspect_review_audio(a.path,max_clips=a.max_clips,
                                       decode_compressed=a.decode_compressed,
                                       overlay_path=a.overlay))
        elif a.review_cmd=="sign-pack":
            from .signed_pack import sign_pack
            _dump(sign_pack(a.path,a.private_key,a.output,
                            require_approved=a.require_approved,overlay_path=a.overlay))
        elif a.review_cmd=="verify-pack":
            from .signed_pack import verify_pack
            _dump(verify_pack(a.signed_file,a.public_key,a.review,overlay_path=a.overlay))
        elif a.review_cmd=="bundle":
            _dump(export_review_bundle(a.path,a.output,include_audio=a.include_audio,
                                       overlay_path=a.overlay))
    elif a.creator_cmd=="events":
        allowed=set(event_profile_for_model(a.model)["known_event_ids"]) if a.model else None
        rows=[]
        for e in events():
            if allowed is not None and int(e["id"]) not in allowed:continue
            if a.category and e.get("category")!=a.category:continue
            rows.append(e)
        _dump(rows)

def _credential_parser(sub):
    c=sub.add_parser("credential",help="Store robot tokens in the OS secret store")
    cs=c.add_subparsers(dest="credential_cmd",required=True)
    s=cs.add_parser("save");s.add_argument("name");s.add_argument("--token")
    s=cs.add_parser("status");s.add_argument("name")
    s=cs.add_parser("delete");s.add_argument("name")

def _credential_main(a):
    if a.credential_cmd=="save":
        token=a.token or getpass.getpass("TOKEN (32 hex, hidden): ").strip()
        _dump(credentials.save(a.name,token))
    elif a.credential_cmd=="status":
        _dump(credentials.status(a.name))
    elif a.credential_cmd=="delete":
        _dump(credentials.delete(a.name))

def main():
    p=argparse.ArgumentParser(prog="vvh",description=f"Vacuum Voice Hub {__version__}")
    p.add_argument("--version",action="version",version=__version__)
    sub=p.add_subparsers(dest="cmd",required=True)

    s=sub.add_parser("list");s.add_argument("--language");s.add_argument("--adult",action="store_true")
    sub.add_parser("stats")
    s=sub.add_parser("models",help="List, search or filter supported research profiles")
    s.add_argument("--search",help="Filter by model ID, name or vendor (case-insensitive)")
    s.add_argument("--vendor",help="Filter by vendor name")
    s.add_argument("--adapter",choices=["dreame_numeric","roborock_legacy","ijai_zip","semantic_bundle"])
    s.add_argument("--hardware-verified",action="store_true",help="Only physically verified VVH models")
    sub.add_parser("languages",help="List attributed prerecorded voices and text-only script locales")
    scripts=sub.add_parser("scripts",help="Model-aware translated recording scripts and offline synthesis")
    script_sub=scripts.add_subparsers(dest="scripts_cmd",required=True)
    script_sub.add_parser("list",help="List text-only script locales")
    sp=script_sub.add_parser("scaffold",help="Generate a translator reference template for model events")
    sp.add_argument("--language",required=True)
    sp.add_argument("--model",default="dreame.vacuum.r2209")
    sp.add_argument("--limit",type=int,default=256)
    sp.add_argument("--output",required=True,help="New JSON file, refuses overwrite")
    sp=script_sub.add_parser("audit",help="Review translated text coverage and provenance")
    sp.add_argument("--language",required=True)
    sp.add_argument("--model",default="dreame.vacuum.r2209")
    sp.add_argument("--overlay",help="Local vvh.translation-overlay.v1 with attributed phrases")
    for script_name in ("show","export"):
        sp=script_sub.add_parser(script_name)
        sp.add_argument("--language",required=True,help="Script locale, e.g. ru, uk, en, zh-Hans")
        sp.add_argument("--model",default="dreame.vacuum.r2209")
        sp.add_argument("--overlay",help="Local reviewed/unreviewed translation overlay JSON")
        if script_name=="export":
            sp.add_argument("--output",required=True,help="New UTF-8 JSON file; refuses overwrite")
    sp=script_sub.add_parser("review-init",help="Create immutable pending language review")
    sp.add_argument("--language",required=True)
    sp.add_argument("--model",default="dreame.vacuum.r2209")
    sp.add_argument("--overlay")
    sp.add_argument("--output",required=True)
    sp=script_sub.add_parser("review-audit",help="Validate exact-script human translation decisions")
    sp.add_argument("path")
    sp.add_argument("--overlay")
    sp=script_sub.add_parser("review-mark",help="Create a new reviewed translation snapshot")
    sp.add_argument("path")
    sp.add_argument("--semantic",required=True)
    sp.add_argument("--status",required=True,choices=["pending","needs-changes","approved"])
    sp.add_argument("--reviewer")
    sp.add_argument("--note")
    sp.add_argument("--language-attested",action="store_true")
    sp.add_argument("--overlay")
    sp.add_argument("--output",required=True)
    sp=script_sub.add_parser("synth",help="Opt-in offline espeak-ng WAV synthesis into Creator workspace")
    sp.add_argument("--language",required=True)
    sp.add_argument("--model",default="dreame.vacuum.r2209")
    sp.add_argument("--id",required=True,dest="pack_id",help="New Creator workspace id")
    sp.add_argument("--author",required=True)
    sp.add_argument("--voice",required=True,help="Exact local espeak-ng voice ID; no automatic fallback")
    sp.add_argument("--speed",type=int,default=160)
    sp.add_argument("--pitch",type=int,default=50)
    sp.add_argument("--output")
    sp.add_argument("--allow-synthetic",action="store_true",help="Explicitly consent to locally generating synthetic WAVs")
    sp.add_argument("--overlay",help="Local translation overlay for extra voice events")
    sp=script_sub.add_parser("piper",help="Generate local WAVs from a user-supplied Piper .onnx voice (no download)")
    sp.add_argument("--language",required=True)
    sp.add_argument("--model",default="dreame.vacuum.r2209")
    sp.add_argument("--id",required=True,dest="pack_id")
    sp.add_argument("--author",required=True)
    sp.add_argument("--voice-model",required=True,help="Existing local .onnx path, with matching .onnx.json")
    sp.add_argument("--output")
    sp.add_argument("--speaker",type=int)
    sp.add_argument("--allow-synthetic",action="store_true")
    sp.add_argument("--overlay",help="Local translation overlay for extra voice events")
    s=sub.add_parser("model-info");s.add_argument("model_id")
    s=sub.add_parser("model-compare",help="Research-only comparison of two robot voice-event profiles");s.add_argument("left_model");s.add_argument("right_model")
    s=sub.add_parser("info");s.add_argument("voice_id")
    s=sub.add_parser("coverage");_add_build_args(s)
    s=sub.add_parser("build");_add_build_args(s)
    s=sub.add_parser("install");_add_build_args(s);s.add_argument("--ip",required=True);_add_auth_args(s);s.add_argument("--allow-experimental-transport",action="store_true")
    s=sub.add_parser("web");s.add_argument("--port",type=int,default=8787)
    sub.add_parser("desktop")
    sub.add_parser("doctor")
    s=sub.add_parser("detect");s.add_argument("--ip",required=True);_add_auth_args(s)
    s=sub.add_parser("import-pack");s.add_argument("path");s.add_argument("--model",default="dreame.vacuum.r2209");s.add_argument("--format",default="auto",choices=["auto","dreame-canonical-ogg","robovoice-r2567r-mp3","ijai-named-mp3","roborock-named"]);s.add_argument("--output")
    research=sub.add_parser("research",help="Offline package research and existing source backlog")
    research_sub=research.add_subparsers(dest="research_cmd")
    s=research_sub.add_parser("inspect",help="Inventory candidate and optionally cross-check package evidence")
    s.add_argument("path")
    s.add_argument("--model",required=True)
    s.add_argument("--evidence",help="Path to vvh.transport-evidence.v1 JSON report")
    s=research_sub.add_parser("validate-evidence",help="Validate local transport evidence without installing")
    s.add_argument("path")
    s.add_argument("--model",help="Require exact model id")
    s=research_sub.add_parser("evidence-bundle",help="Make metadata-only firmware evidence ZIP")
    s.add_argument("report")
    s.add_argument("--package",required=True,help="Local candidate package; not included in ZIP")
    s.add_argument("--output",required=True)
    s=research_sub.add_parser("verify-evidence-bundle",help="Check ZIP and actual current package SHA-256")
    s.add_argument("path")
    s.add_argument("--package",required=True)
    s.add_argument("--model")
    s=research_sub.add_parser("hardware-scaffold",help="Create unapproved metadata-only hardware-test report offline")
    s.add_argument("--model",required=True,help="Exact canonical model ID")
    s.add_argument("--firmware",required=True,help="Non-sensitive firmware version; never a token")
    s.add_argument("--package",required=True,help="Local candidate; hashed, never included in report")
    s.add_argument("--output",required=True,help="New JSON path; refuses overwrite")
    s=research_sub.add_parser("hardware-acceptance",help="Assess model, firmware and rollback evidence only")
    s.add_argument("path")
    s.add_argument("--model",help="Require exact canonical model ID")
    s=sub.add_parser("preview");s.add_argument("voice_id");s.add_argument("--model",default="dreame.vacuum.r2209");s.add_argument("--play",action="store_true")
    s=sub.add_parser("stock");s.add_argument("--model",default="dreame.vacuum.r2209");s.add_argument("--manifest-url")
    s=sub.add_parser("restore-stock");s.add_argument("stock_id");s.add_argument("--model",default="dreame.vacuum.r2209");s.add_argument("--ip",required=True);_add_auth_args(s);s.add_argument("--manifest-url");s.add_argument("--allow-experimental-transport",action="store_true")
    s=sub.add_parser("history");s.add_argument("--limit",type=int,default=50)
    s=sub.add_parser("report");s.add_argument("--ip",required=True);_add_auth_args(s);s.add_argument("--model");s.add_argument("--output")
    s=sub.add_parser("validate-report");s.add_argument("path")
    release=sub.add_parser("release",help="Build or verify reproducible release bundles")
    rs=release.add_subparsers(dest="release_cmd",required=True)
    s=rs.add_parser("build");s.add_argument("--output",default="release");s.add_argument("--source-date-epoch",type=int)
    s=rs.add_parser("verify");s.add_argument("path",nargs="?",default="release")
    site=sub.add_parser("site",help="Build or verify the static public catalog")
    ss=site.add_subparsers(dest="site_cmd",required=True)
    s=ss.add_parser("build");s.add_argument("--output",default="public")
    s=ss.add_parser("verify");s.add_argument("path",nargs="?",default="public")
    _creator_parser(sub)
    _credential_parser(sub)

    a=p.parse_args()
    if a.cmd=="creator":return _creator_main(a)
    if a.cmd=="credential":return _credential_main(a)
    if a.cmd=="release":
        return _dump(build_release(a.output,a.source_date_epoch) if a.release_cmd=="build" else verify_release(a.path))
    if a.cmd=="site":
        return _dump(build_site(a.output) if a.site_cmd=="build" else verify_site(a.path))

    if a.cmd=="scripts":
        from .script_packs import list_locales, script_for_model, synthesize_workspace
        if a.scripts_cmd=="list":return _dump(list_locales())
        if a.scripts_cmd=="scaffold":
            from .translation_overlays import translation_scaffold
            from pathlib import Path
            result=translation_scaffold(a.language,a.model,a.limit)
            dest=Path(a.output).expanduser().resolve()
            dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open("x",encoding="utf-8") as stream:
                stream.write(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
            return _dump({"output":str(dest),"candidate_count":result["candidate_count"],
                          "translated_entries":0,"install_authorized":False})
        if a.scripts_cmd in ("review-init","review-audit","review-mark"):
            from .language_review import (create_language_review, audit_language_review,
                                          mark_language_review)
            if a.scripts_cmd=="review-init":
                return _dump(create_language_review(a.language,a.model,a.output,
                                                    overlay_path=a.overlay))
            if a.scripts_cmd=="review-audit":
                return _dump(audit_language_review(a.path,overlay_path=a.overlay))
            return _dump(mark_language_review(a.path,a.semantic,a.status,a.output,
                                              reviewer=a.reviewer,note=a.note,
                                              language_attested=a.language_attested,
                                              overlay_path=a.overlay))
        if a.scripts_cmd=="audit":
            report=script_for_model(a.language,a.model,a.overlay)
            return _dump({k:report[k] for k in ("schema","locale","model_id","scripted_count",
                         "mapped_count","model_event_count","mapped_event_count",
                         "model_event_coverage_pct","overlay_count","overlay_attribution",
                         "unmapped_semantics","model_install_authorized")})
        if a.scripts_cmd in {"show","export"}:
            result=script_for_model(a.language,a.model,a.overlay)
            if a.scripts_cmd=="show":return _dump(result)
            from pathlib import Path
            dest=Path(a.output).expanduser().resolve()
            dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open("x",encoding="utf-8") as stream:
                stream.write(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
            return _dump({"output":str(dest),"locale":a.language,
                          "mapped_count":result["mapped_count"],"scripted_count":result["scripted_count"],
                          "audio_files_generated":False})
        if a.scripts_cmd=="piper":
            from .piper_studio import synthesize_piper_workspace
            return _dump(synthesize_piper_workspace(a.language,a.model,a.pack_id,a.author,
                                                     a.voice_model,output=a.output,
                                                     speaker=a.speaker,
                                                     allow_synthetic=a.allow_synthetic,
                                                     overlay_path=a.overlay))
        return _dump(synthesize_workspace(a.language,a.model,a.pack_id,a.author,a.voice,
                                         output=a.output,speed=a.speed,pitch=a.pitch,
                                         allow_synthetic=a.allow_synthetic,overlay_path=a.overlay))
    if a.cmd=="languages":
        from .script_packs import list_locales
        recorded={}
        for v in voices():recorded[v["language"]]=recorded.get(v["language"],0)+1
        return _dump({"recorded_variants":recorded,"recorded_language_count":len(recorded),
                      "text_only_script_locales":list_locales(),
                      "script_templates_are_recordings":False})
    if a.cmd=="list":
        for v in voices():
            if a.language and v["language"]!=a.language:continue
            if a.adult and not v.get("adult"):continue
            flag=" 🔞" if v.get("adult") else ""
            print(f"{v['id']:<30} {v['language']:<3} {v.get('source_verification','unknown'):<22} {v['title']}{flag}")
    elif a.cmd=="stats":
        vv=voices();mm=models()
        _dump({
            "version":__version__,"voices":len(vv),"adult":sum(bool(v.get("adult")) for v in vv),
            "languages":sorted(set(v["language"] for v in vv)),"models":len(mm),
            "hardware_verified_models":sum(bool(m.get("device_tested")) for m in mm),
            "install_default_models":sum(bool(m.get("transport",{}).get("allow_default")) for m in mm),
            "semantic_events":len(events()),"semantic_categories":categories(),
            "target_combinations":len(vv)*len(mm),
            "text_script_pack_schema":"vvh.script-pack.v1",
            "adapters":sorted({m.get("adapter") for m in mm}),
            "creator_schema":"vvh.voicepack.v1","compat_report_schema":"vvh.compat-report.v1","public_catalog_schema":"vvh.public-catalog.v1","release_manifest_schema":"vvh.release-manifest.v1","update_feed_schema":"vvh.update-feed.v1",
            "research_backlog":len(backlog()),
        })
    elif a.cmd=="models":
        count=0
        for m in models():
            if a.search and a.search.casefold() not in (" ".join((m["id"],m["name"],m.get("vendor","")))).casefold():continue
            if a.vendor and a.vendor.casefold() not in m.get("vendor","").casefold():continue
            if a.adapter and a.adapter!=m.get("adapter"):continue
            if a.hardware_verified and not m.get("device_tested"):continue
            t=m.get("transport",{})
            print(f"{m['id']:<30} {m['name']:<32} adapter={m.get('adapter','-'):<16} transport={t.get('verification','-')}")
            count+=1
        if not count:print("No matching model profiles")
    elif a.cmd=="model-compare":
        from .model_discovery import compare_models
        return _dump(compare_models(a.left_model,a.right_model))
    elif a.cmd=="model-info":_dump(model_by_id(a.model_id))
    elif a.cmd=="info":_dump(voice_by_id(a.voice_id))
    elif a.cmd in {"coverage","build","install"}:
        fbc=_parse_category_fallbacks(a.fallback_category)
        if a.cmd=="coverage":
            b=build_voice(a.voice_id,a.model,fallback_voice_id=a.fallback,fallback_categories=fbc,package_output=False)
            _dump({"voice_id":a.voice_id,"model":b["model"],"compatibility":b["compatibility"],"original_compatibility":b["original_compatibility"],"fallbacks":b.get("fallbacks")})
        elif a.cmd=="build":_dump(build_voice(a.voice_id,a.model,fallback_voice_id=a.fallback,fallback_categories=fbc))
        else:_dump(install_voice(a.voice_id,a.model,a.ip,_resolve_token(a),fallback_voice_id=a.fallback,fallback_categories=fbc,allow_experimental_transport=a.allow_experimental_transport))
    elif a.cmd=="web":serve(a.port)
    elif a.cmd=="desktop":
        from .desktop import main as desktop_main
        desktop_main()
    elif a.cmd=="research":
        if a.research_cmd=="inspect":
            from .research_pipeline import ResearchError,assess_candidate
            from .archive_inspector import ArchiveInspectionError
            try:
                _dump(assess_candidate(a.path,a.model,evidence_path=a.evidence))
            except (ResearchError,ArchiveInspectionError,KeyError,ValueError,OSError) as exc:
                raise SystemExit(f"research inspect failed: {exc}") from exc
        elif a.research_cmd=="evidence-bundle":
            from .firmware_evidence_bundle import create_evidence_bundle
            _dump(create_evidence_bundle(a.report,a.package,a.output))
        elif a.research_cmd=="verify-evidence-bundle":
            from .firmware_evidence_bundle import verify_evidence_bundle
            _dump(verify_evidence_bundle(a.path,a.package,expected_model=a.model))
        elif a.research_cmd=="hardware-scaffold":
            from .community_testkit import create_hardware_scaffold
            _dump(create_hardware_scaffold(a.model,a.firmware,a.package,a.output))
        elif a.research_cmd=="hardware-acceptance":
            from .hardware_acceptance import inspect_acceptance_file
            _dump(inspect_acceptance_file(a.path,expected_model=a.model))
        elif a.research_cmd=="validate-evidence":
            from .transport_evidence import EvidenceError,inspect_file
            try:
                _dump(inspect_file(a.path,expected_model=a.model))
            except (EvidenceError,OSError) as exc:
                raise SystemExit(f"research evidence failed: {exc}") from exc
        else:
            for x in backlog():print(f"{x['status']:<38} {x['title']} — {x.get('source_page','')}")
    elif a.cmd=="preview":
        f=preview_file(a.voice_id,a.model);print(f)
        if a.play:
            import subprocess,sys
            player="afplay" if sys.platform=="darwin" else "ffplay"
            subprocess.run([player,str(f)])
    elif a.cmd=="stock":
        r=list_stock(a.model,a.manifest_url);print("manifest:",r["manifest"]);[print(f"{x['id']:<18} {x['size']:>9}  {x['url']}") for x in r["items"]]
    elif a.cmd=="restore-stock":
        r=list_stock(a.model,a.manifest_url);item=next((x for x in r["items"] if x["id"]==a.stock_id),None)
        if not item:raise SystemExit(f"stock id not found: {a.stock_id}")
        _dump(install_stock(a.model,a.ip,_resolve_token(a),item,allow_experimental_transport=a.allow_experimental_transport))
    elif a.cmd=="detect":_dump(miot.info(a.ip,_resolve_token(a)))
    elif a.cmd=="import-pack":_dump(convert_local(a.path,a.model,a.format,a.output))
    elif a.cmd=="history":_dump(load_history(a.limit))
    elif a.cmd=="report":
        _dump(write_report(build_report(a.ip,_resolve_token(a),a.model),a.output))
    elif a.cmd=="validate-report":
        from pathlib import Path
        data=json.loads(Path(a.path).read_text(encoding="utf-8"))
        _dump(validate_report(data))
    elif a.cmd=="doctor":
        import shutil,sys
        print("python:",sys.version.split()[0])
        print("ffmpeg:",shutil.which("ffmpeg") or "bundled via imageio-ffmpeg after install")
        print("ccrypt:",shutil.which("ccrypt") or "optional; required only for legacy Roborock .pkg")
        print("voices:",len(voices()));print("models:",len(models()));print("events:",len(events()))
        print("creator: vvh.voicepack.v1");print("reports: vvh.compat-report.v1");print("public catalog: vvh.public-catalog.v1");print("release manifest: vvh.release-manifest.v1");print("update feed: vvh.update-feed.v1");print("OK")
