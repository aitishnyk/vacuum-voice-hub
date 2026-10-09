# Changelog

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
