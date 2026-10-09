# Roadmap

## Current v0.21 audio-production wave

Implemented in source: offline master-preview directory batch processing, per-source SHA-256, collision-safe filenames, bounded max 256 files and deletion of incomplete NEW batch outputs. Before release, verify full Python CI, CodeQL, Public Site, reproducible bundle and macOS/Windows/Linux packaging. Hardware/community tests remain a separate workstream; shipping tested software never implies new physical-device approval.

## Completed

- v0.1 — X10 foundation ✅
- v0.2 — 55 Voice Wave + Compatibility ✅
- v0.3 — Multi-model foundation ✅
- v0.4 — Creator Studio ✅
- v0.5 — Desktop + Community Verification ✅
- v0.6 — Public Catalog ✅
- v0.7 — Distribution Hardening ✅
- v0.8 — 109-model Mass Expansion ✅
- v0.9 — Offline Research Infrastructure (schemas, inspect, evidence cross-check, CLI, regressions) ✅ software scope
- v0.9.1 — Safe local archive extraction on Python 3.10+ ✅ source scope
- v0.10.0 — 154-model discovery, 18 text-script locales, opt-in offline voice synthesis ✅ software scope
- v0.11.0 — Offline Piper neural TTS (user-supplied model) + WAV/Creator Audio QA ✅ software scope
- v0.12.0 — User-attributed localization overlays + scaffold + per-model script coverage ✅ software scope
- v0.13.0 — 215-model five-brand discovery, identity preservation and research-only comparison ✅ software scope
- v0.14.0 — Creator per-target preflight and offline 1–16-model batch output with SHA-256 ✅ software scope
- v0.15.0 — Optional bounded compressed QA, gain preview and actual locale/audio coverage ✅ software scope
- v0.16.0 — Recording assignments, tamper-aware human review, private-by-default ZIP export ✅ software scope
- v0.17.0 — Safe reviewer import with no extracted ZIP files, hash history, firmware+rollback evidence ✅ software scope
- v0.18.0 — Optional user-key Ed25519 reviewed-audio attestation, per-clip QA and evidence Studio ✅ software scope
- v0.19.0 — Whole-pack Ed25519 source manifest and metadata-only firmware evidence bundle ✅ software scope

## v0.9 — Offline Research Infrastructure

Implemented in source:
- offline evidence intake with strict SHA-256, size, source and exact-model checking;
- bounded ZIP/TAR audio package inventory and opaque proprietary package fingerprinting;
- filename-based layout heuristics and event-profile comparison;
- versioned JSON schemas, CLI and negative security tests;
- explicit *never authorize installation from research evidence* boundaries.

Hardware/package-adapter work formerly listed under v0.9 is **not** marked complete. The offline research stage enables the subsequent exact-device work without guessing vendor protocols.

## v0.11 — Offline Piper and Audio QA

Implemented: local Piper synthesis via an existing voice ONNX/config, opt-in Creator workspace generation; read-only WAV signal QA and a Creator interface button. No automatic voice-model download or install.

Deferred improvements:
- richer localized script coverage beyond the 16 essential prompts, reviewed per language;
- more source-backed model IDs from public integrations, preserving aliases;
- archive/event-layout fingerprints and per-model source fixture attribution;
- Creator UX for recording review, pronunciation QA and multi-locale project export;
- hardware-verified transport updates only where exact-device acceptance evidence exists.

## v0.12 — Local Translation Overlay Studio

Implemented: bounded local user overlays, model-specific English reference scaffold, audited locale coverage, and optional use of the translated events in both local TTS engines. Human review and distribution rights are still required.

## v0.13 — Multi-Brand Model Discovery

Implemented: 61 additional MIoT-listed device identities, research-only portable profiles, original 154-device preservation snapshot, and model compare with provenance. Physical install transports are not thereby verified.

## v0.14 — Creator Voice-Pack Preflight & Batch QA

Implemented: read-only per-target mapping/missing-core/collision diagnostics and independent offline 1–16-model packaged outputs with source SHA-256 and a batch manifest. Research-only hardware policies remain unchanged.

## v0.15 — Compressed Audio Signal QA & Language Coverage

Implemented bounded opt-in FFmpeg decode QA, non-destructive WAV gain preview, and model-aware translated-text-versus-assigned-audio reporting. No new device format claims.

## v0.16 — Voice Production Workflow & Human Review

Implemented: every-event recording assignments, explicit human acknowledgement/rights attestation, SHA-256 checks, safe resnapshot and private-by-default metadata export. Human declarations are not independently verified credentials or legal rights.

## v0.17 — Returned Reviewer Handoff & Hardware Evidence

Implemented: returned review JSON/ZIP checked against original workspace, safe untrusted-claim import, hash-linked local history and fail-closed model+firmware acceptance intake. Device authorization requires independently proven future adapter work.

## v0.18 — Reviewer key attestations and human/signal evidence

Implemented detached Ed25519 verification with independently provided PEM keys, current source/review validation and local bounded per-clip signal QA. Firmware evidence is only assessed, not physically accepted.

## v0.19 — Signed Voice Asset Source & Firmware Evidence

Completed software scope: Ed25519 whole-pack manifest of all assigned source audio and human review states; metadata-only firmware candidate evidence ZIP with current package SHA verification and explicit non-authorizing status. Hardware proof is still separate.

## v0.20 — Implemented community-first intake and audio/language foundation

Implemented: new model identities (not verified transports), text templates, local master-preview and GitHub issue templates for community tests/donated hardware. Continuing: licensed locale/native-speaker review, independent firmware/rollback acceptance, pronunciation QA and signed distribution review. Software stable releases may ship before all hardware has been tested, with conservative labels.

## v1.0 — Verified Transport & Real-Device Acceptance (external evidence required)

Pending evidence-backed tasks:
- ROIDMI EVA / EVE package format and set-voice payload;
- Xiaomi H40 / M30 / M40 / X20+ exact voice package and transport;
- Mijia 5/6 models with lawful, source-attributed stock pack references;
- Viomi Alpha/V3 and newer Dreame S10/X10/W10 event mappings;
- additional IJAI exact-device MIoT action verification;
- hardware-backed acceptance reports, repeatability and firmware regressions;
- optional legacy Roborock ccrypt packaging replacement only after interoperability and legal review.

Do not claim any of these finished by publishing the research tooling. No new hardware proof is created by running automated tests.

## v1.0 readiness

v1.0 is evidence-driven, not a version-number exercise.

Do not claim:
- hardware verified without physical evidence;
- custom install on vendor-signed generations;
- signed/notarized binaries without real signatures;
- universal package compatibility when only semantic/build support exists.
