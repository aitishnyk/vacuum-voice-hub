# Changelog

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
