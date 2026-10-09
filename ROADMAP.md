# Roadmap

## v1.7 — Offline adapter interchange (source increment)

Real user-defined adapter descriptor, deterministic byte-verified ZIP builder, CLI preflight and archive verifier. This does not produce an official signed vacuum package or authorize installation. [Guide](docs/ADAPTER_INTERCHANGE_V170.md).


## v1.6 — Community research moderation (local source release)

A functioning local privacy-conscious inbox imports exact hardware evidence JSON, hashes and redacts submissions, logs human research decisions in new copy-on-write snapshots with SHA-linked history; it never certifies hardware. [Docs](docs/COMMUNITY_INBOX_V160.md). A hosted moderation website, a donated-device logistics portal and independent hardware acceptance are not claimed.


## v1.5 — Audio Timeline (implemented first Creator 2.0 wave)

Working local waveform canvas, start/end selector and non-destructive WAV export inside Creator Studio, plus bounded deterministic Python CLI cut-preview. This is not full multitrack DAW, LUFS mastering or automatic audio approval. [Documentation](docs/AUDIO_TIMELINE_V150.md).


## v1.4 — Model & Firmware Evidence Matrix (offline software wave)

Strict per-model and per-firmware self-report reconciliation for up to 64 local reports, with digest validation and conflicting evidence flags. This does NOT authorize any new hardware/firmware installation. [Guide](docs/FIRMWARE_MATRIX_V140.md). Broader hardware adapter verification remains community-driven and pending.


## v1.3 — Pronunciation Lexicon (implemented initial wave)

User-provided strict locale lexicon, one-pass spoken substitutions for Piper/eSpeak and read-only preview with SHA-256 provenance. Expanded audited multilingual semantic coverage and full independent native-speaker reviews remain pending. See [guide](docs/PRONUNCIATION_V130.md).


## v1.2 — Language Review & Audio A/B (software scope)

Implemented offline attributed translation review (stale-script detection, copy-on-write approvals) and read-only local audio A/B metrics. Future v1.2.x work: GUI waveform editor, professional LUFS/true-peak mastering, noise-floor analysis and multi-locale native proofreading, with independent QA per feature. See [documentation](docs/AUDIO_LANGUAGE_REVIEW_V120.md).

## Planned v1.3 → v2.0 (NOT implemented)

- v1.3: native-speaker-supported multilingual TTS expansion, semantic event coverage and pronunciation references.
- v1.4: stronger source-attributed model+firmware capability index; no automatic hardware transport promotion.
- v1.5: visual, non-destructive Creator timeline, QA and export UX.
- v1.6: moderated community evidence workflow and optional donated device acceptance.
- v1.7: safe format/event adapter SDK with per-model tests and explicit evidence requirements.
- v1.8: rights-aware licensed voice library, credit/license provenance and signed distributions.
- v1.9: desktop release polish, recovery, signing/notarization where actually available, security hardening.
- v2.0: integrated stable Universal Voice Studio, release migration and platform API certification. Research support does not imply universal installation.


## v1.1 — Community hardware intake automation (SOFTWARE STABLE / SOURCE SEALED)

Implemented and CI-certified: generate a safe unapproved metadata-only SHA-256 hardware report using `vvh research hardware-scaffold`, collect five real observed test steps only with redacted HTTPS evidence, and have maintainers manually review each exact model+firmware before any transport policy change. Retain software CI and community-first optional donated/loaned hardware. Future: simplify translation proofreading, expand true firmware event mappings and add more DAW-like audio editing with preservation/rights checks.

## v1.0 SOFTWARE STABLE / SOURCE SEALED

Completed source/core software milestone: 223 preserved model identity profiles, 55 attributed voice variants, 22 text-script locales, single/batch offline mastering, safety/review/Ed25519 provenance and CI-enforced baseline audit. Exact PR-head 250/250 tests, public site, release bundle, CodeQL and Windows/macOS/Linux desktop packages PASS. Merged-main Python CI/CodeQL/Public Site also PASS. Device installation is **not** certified across 223 models; ongoing community reports and voluntary donated/loaned hardware can expand evidence per exact model and firmware.

## Previous v1.0 stable software scope

Goal: stable public offline editor, model/locale catalogs and signed/reviewed audio production pipeline on Windows/macOS/Linux, with independent source audit and exact-head CI/CodeQL. Physical-device verification is a separate evidence stream operated with community volunteers; manufacturers or supporters may optionally contribute devices without editorial influence. 223 models mean researched identities, not 223 verified installers. After stable source release, additional physical transports, native-speaker verified recordings, and more advanced Creator UX continue as individually verified v1.x features.

## Previous v0.21 audio-production wave

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
