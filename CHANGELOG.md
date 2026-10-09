# Changelog

## 1.0.0 — 2026-10-09 (SOFTWARE STABLE / SOURCE SEALED after exact-head and merged-main CI acceptance)

- Stabilized offline software contracts and introduced a machine-readable `vvh.software-stable-audit.v1` gate in CI for all 223+ model profiles, 55 credited voice variants, 22+ text languages and preserved old model IDs/aliases.
- Source/audio mastering and batch mastering remain opt-in, non-destructive and subject to human listening and licensing; package signatures do not certify devices or redistribution rights.
- Community on-device hardware evidence, failures and voluntary manufacturer/user hardware loans/donations are tracked independently of software build gates.
- Exact PR-head and merged-main GitHub Actions acceptance still required before calling this source release SEALED; no new physical device install permission or commercial fork code.

## 0.21.0 — 2026-10-09 (source candidate, batch audio production)

- New offline `vvh creator master-batch` command for up to 256 audio clips per new batch output.
- Independent WAV previews with SHA-256 provenance, deterministic manifest and atomic cleanup on any clip failure.
- Case-insensitive output collision detection, symlink input refusal, no source overwrites and no automatic install.
- Preserve 223 researched profiles, 55 original voice variants, 22 text locales and community-first hardware intake.

## 0.20.0 — 2026-10-09 (source candidate, community and audio production)

- 223 model identities (+8 MIoT-index research-only profiles); 55 original voice variants preserved and hardware install authorization unchanged.
- 22 text-script locales (+Indonesian, Vietnamese, Arabic and Hindi, 16 reference phrases each), separate from recorded/audio availability and awaiting community language review.
- New `vvh creator master-preview`: local bounded decoding, trim/padding/fades, max +12 dB gain, exclusive WAV creation and SHA-256/QA evidence, without editing source recordings.
- Community model/firmware/rollback evidence and manufacturer/volunteer loan or donation issue templates; no commercial Telegram, Bunny or payment code.
- Physical support remains Xiaomi X10-only until independent evidence for another model.

## 0.19.0 — 2026-10-09 (signed pack source and firmware evidence bundle)

- introduced user-key Ed25519 `vvh.signed-pack-manifest.v1` covering every assigned source clip hash, mapped semantic/event IDs, text digest, model, locale and explicit human review status; signed timestamp included;
- whole-pack verification reloads Creator and review from disk, refuses changed audio, mappings, translations, reviewer states and signatures. `--require-approved` provides fail-closed human signoff policy;
- metadata-only `vvh.firmware-evidence-bundle.v1` ZIP reports exact model, firmware, local candidate package SHA-256 and size plus five documented research observations; no proprietary firmware binary/robot credentials in ZIP;
- evidence verification rejects altered local candidate packages, extra ZIP members and modified report/assessment/manifest fields without changing installer policy;
- maintained original 215 models, 55 credited voice variants, 18 text-only locales, frozen 109/154 identity fixtures and Xiaomi X10-only physical installation acceptance.

## 0.18.0 — 2026-10-09 (reviewer provenance and evidence UI)

- optional locally user-supplied Ed25519 PEM signing and detached verification of explicitly approved per-event human reviews, bound to the exact recording SHA-256, model, script digest and reviewer claim;
- verify signatures against a separate public key while recomputing present Creator audio and source review; signed claims never prove legal rights, actual language or manufacturer upload support;
- bounded read-only per-clip Creator review signal QA reports WAV plus opt-in FFmpeg-decoded audio alongside independent human statuses;
- Creator Studio adds a per-model evidence checklist for signature review, voice download/playback, reboot persistence and tested stock-voice rollback; assessment is always research-only;
- signing dependency is optional for bare CLI and explicitly included in CI and three desktop build artifacts;
- all 215 canonical model IDs, 55 original attributed voices, 18 script locales and X10-only physical hardware evidence unchanged.

## 0.17.0 — 2026-10-09 (returned reviewer handoff and evidence boundary)

- added local `vvh creator review import` for returned JSON/ZIP with strict file bounds, duplicate/path/symlink checks, no filesystem ZIP extraction and exact Creator/project/model/script/audio SHA-256 reconciliation;
- returned reviewer statuses/rights declarations stay separately labeled untrusted external claims; local review decisions reset to draft instead of automatically trusting remote approval;
- SHA-256-linked, local bounded review-event history records marking/refresh/import; detects inconsistent chains but is not cryptographically signed;
- Creator Studio adds small metadata handoff import and history inspection through existing authenticated localhost session;
- model+firmware+package/rollback evidence intake never modifies install policies, and even a complete self-report remains independent-review-only;
- preserved all 215 source-backed models, 55 attributed source voices, 18 text locales, 109/154 fixtures and X10-only verified hardware.

## 0.16.0 — 2026-10-09 (voice recording workflow and human review)

- exported recording assignments for every known semantic event of a selected 215-model profile, including untranslated English references and optional user overlay;
- added independently tracked `draft → recorded → listened → approved` workflow with human reviewer, explicit language and redistribution-rights attestations;
- persisted SHA-256 of each source recording and source Creator manifest; audit rejects stale files, reassigned events and modified text, while refresh resets only the changed tasks;
- introduced metadata-only default review ZIP and explicit opt-in local audio inclusion with total-size caps and integrity checks;
- integrated recording checklist, status, refresh, hash audit and ZIP export into localhost Creator Studio;
- no new vendor custom-install support or audio licensing inferred; all 215 models, 55 recorded catalog voice variants, 18 text locales and Xiaomi X10-only physical evidence preserved.

## 0.15.0 — 2026-10-09 (advanced audio QC and language truth)

- offline bounded opt-in FFmpeg decoding of compressed OGG/MP3/FLAC/M4A/AAC/Opus to temporary 16-bit PCM with timeout, byte/duration caps and signal heuristics;
- Creator workspace Audio QA, per-model preflight and batch-build optional compressed-source review, defaults unchanged;
- gain-only, non-destructive WAV preview export with before/after loudness and SHA-256;
- actual per-model `language-coverage` report separates translated text, assigned audio and declared language; never claims speaker language or licensing verified;
- read-only localhost coverage endpoint, Creator UI checkboxes for compressed decoding and text-vs-audio comparison;
- preserved all 215 device profiles, 55 audio variants, 18 text script locales and Xiaomi X10-only physical hardware verification.

## 0.14.0 — 2026-10-09 (Creator adaptation and batch-build QA)

- added offline `vvh creator preflight` per-model event mapping, source SHA-256, missing core prompts, duplicate-event conflicts and optional WAV quality warnings;
- added `vvh creator batch` to build 1–16 independent target-adapter packages from a single Creator workspace, including SHA-256 manifest;
- output directories must be new; duplicate canonical targets and unsafe/ambiguous inputs fail closed; partial batch is cleaned without changing source project;
- added localhost Creator Studio preflight and authenticated multi-model build endpoints/buttons;
- unchanged 215 model identities, 55 original attributed audio variants, 18 text-script locales and X10-only physically verified VVH custom install.

## 0.13.0 — 2026-10-09 (source-backed multi-brand discovery)

- merged 61 publicly attributed MIoT model identities: 26 Viomi, 19 Xiaomi/Mijia, 9 Roborock, 4 ROIDMI, 3 IJAI;
- total 215 canonical profiles, preserving all 154 previous profiles and aliases and original 55 source-linked audio voice variants;
- all 61 new profiles only expose portable semantic research/build/preview, with custom-install blocked even in experimental mode;
- added `vvh model-compare` with event-ID overlap, adapter/container comparison, provenance and explicit no-install-certification result;
- published v0.12 frozen model ID/alias/adapter/transport test fixture; updated matrix tests, package mirror and audit to detect model loss;
- no invented product/plugin numbers, firmware verification, vocal recordings, transport permissions or vendor package decryption.

## 0.12.0 — 2026-10-09 (scalable multilingual semantic voice packs)

- added strictly validated local `vvh.translation-overlay.v1` files with exact language, source/license attribution, bound on file/phrase counts and known semantic event validation;
- generated source-language reference scaffold for device-specific prompts not yet included in the 16 built-in phrases; English references are explicitly NOT claimed translated;
- CLI `vvh scripts scaffold` and `vvh scripts audit` with model event coverage and explicit local override handling;
- `--overlay` extends preview, export, eSpeak-NG and offline Piper to additional user-translated known events;
- safeguarded all 154 registered device profiles, 55 real attributed variants, 18 core locales, blocked modern device installs, and the X10-only VVH physical-verification boundary.

## 0.11.0 — 2026-10-09 (offline voice quality)

- optional local Piper TTS using user-supplied ONNX voice model and matching config, with exact script-language verification, explicit opt-in and offline subprocess execution;
- local generated 16-event WAV Creator projects with SHA-256 voice-model attribution and license-review warnings; no automatic download or robot installation;
- WAV signal QA: duration, RMS/peak, clipping, silence, malformed/oversized input checks;
- read-only Creator workspace audio QA endpoint, CLI and UI with model-specific coverage;
- existing 154 device profiles, 55 community variants and 18 text-only script locales retained.

## 0.10.0 — 2026-10-09 (model and language software expansion)

- 45 new source-backed Dreame/Xiaomi/MOVA IDs; catalog grows 109 → 154 and software matrix 5,995 → 8,470;
- conservative build/preview-only profiles for new variants, no false custom-install verification;
- preserved every historical model ID/alias and all 55 credited audio voice records; duplicate regional canonical IDs avoided;
- text-only 18-language script templates, 16 translated core events each; exact model-event mapping;
- CLI model filters, script preview/export, local opt-in espeak-ng WAV generation into Creator Studio;
- local read-only script APIs and Creator Studio script preview; public catalog distinguishes prerecorded languages from text templates;
- v0.10 schema, regression tests, audit and release manifest integration; hardware acceptance and binary signing remain separate.

## 0.9.1 — 2026-10-09 (source security release)

- replaced legacy `tar.extractall` / `zip.extractall` with bounded streaming extraction for local voice pack imports on Python 3.10+;
- fail-closed on absolute/traversal/ambiguous paths, symlinks, special members, duplicate/colliding entries and oversized archives;
- added positive/negative archive security regression tests;
- preserved all 109 model IDs, 55 voice variants and evidence-scoped install policies;
- verified exact-main CI, CodeQL, public catalog and PR desktop builds across macOS, Windows and Linux;
- source release sealed; independent hardware-wide installation acceptance and distribution signing remain pending.

## 0.9.0 — 2026-10-09 (offline research workflow)

- added `vvh.transport-evidence.v1` source-report intake with model-identity, SHA-256, size and format constraints;
- added `vvh.archive-inventory.v1` bounded read-only ZIP/TAR inventory;
- introduced `vvh research inspect` and `vvh research validate-evidence` with `vvh.research-assessment.v1` output;
- added event-profile numeric ID comparison, filename-pattern heuristics and opaque proprietary package hashing without decoding/install;
- published three JSON schemas and security-focused tests;
- research reports cannot authorize installation, and no new physical robot has been claimed verified.

## 0.8.0 — 2026-10-08

### Mass Model Expansion
- imported 103 requested Mi Home ecosystem rows;
- expanded catalog from 7 to **109 model profiles**;
- retained exact product/plugin metadata from the supplied inventory;
- software matrix = **109 models × 55 voices = 5,995 target combinations**.

### Target adapters
- Dreame numeric OGG/tar.gz;
- classic Roborock named WAV / encrypted .pkg;
- IJAI named MP3/ZIP;
- portable semantic OGG ZIP for unverified package families.

### Compatibility safety
- added conservative modern-Dreame intersection profile;
- added Roborock semantic profile;
- added IJAI semantic profile;
- added portable semantic core profile;
- compatibility analysis no longer requires target packaging;
- preview now works from canonical audio before vendor packaging.

### Installation transports
- retained verified X10 MIoT property install;
- added experimental Roborock `dnld_install_sound`;
- added experimental IJAI URL+MD5 MIoT action;
- newer signed Roborock models fail closed;
- unknown vendor transports remain build-only.

### UX / QA
- model search in main UI, Creator Studio and public catalog;
- model cards show adapter/container/product/plugin metadata;
- CI model-matrix audit;
- exact family-count and 5,995-combination tests.

## 0.7.0 — 2026-10-08
- reproducible distribution, SPDX SBOM, SHA256SUMS and update feed.

## 0.6.0 — 2026-10-08
- deterministic public catalog.

## 0.5.0 — 2026-10-08
- desktop + community verification.

## 0.4.0 — 2026-10-08
- Creator Studio.

## 0.3.0 — 2026-10-08
- initial multi-model wave.

## 0.2.0 — 2026-10-08
- 55 voice wave.

## 0.1.0 — 2026-10-08
- X10 foundation.
