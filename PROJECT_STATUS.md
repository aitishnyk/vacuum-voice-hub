# Project status — v0.8.0 (source merged)

- Product: **Vacuum Voice Hub**
- Repository: `aitishnyk/vacuum-voice-hub`
- Source version: **v0.8.0**
- Main commit: `25d4720b844ccf343a56ffdfd25f76a7ff1f4d79`
- Functional release PR: **#8 — 109-Model Mass Expansion**
- Model profiles: **109** (103 inventory rows, 102 newly added IDs plus 7 existing profiles)
- Source-attributed voice variants: **55**
- Software target matrix: **5,995 voice × model combinations**
- Families: **32 Dreame numeric, 33 Roborock, 8 IJAI, 36 portable/build-only**
- Physically verified target: **Xiaomi Robot Vacuum X10 (`dreame.vacuum.r2209`) only**
- The remaining targets are **not** claimed hardware-verified; per-target install policy applies.

## Current capabilities

- Semantic voice events, per-target safe filtering and fallback coverage.
- Dreame numeric OGG / `tar.gz` builder.
- Classic Roborock named WAV / `.pkg` builder (external `ccrypt` required).
- IJAI named MP3 / ZIP builder.
- Portable semantic bundles for unverified vendor package formats; `installable=false`.
- Model-aware Creator Studio, local Web UI, CLI, desktop shell, public searchable catalog.
- Privacy-safe community reports and local install history.
- Reproducible source distribution, SPDX SBOM, SHA-256 verification.

## Hardware and install claim boundaries

- X10: local voice transport/package acceptance verified on device; **individual community voices are not universally hardware-certified**.
- Legacy Roborock and documented IJAI transports: experimental; require explicit user opt-in.
- Newer vendor-signed Roborock generations: arbitrary custom installation blocked.
- Unverified Xiaomi/Mijia/Viomi/ROIDMI/Smartmi families: build/preview/coverage only.
- Model names, Mi Home plugin IDs, official voice availability and semantic coverage do **not** prove custom voice install capability.
- Platform binaries must not be described as signed or notarized without actual signing evidence.

## Validation record

The v0.8.0 PR description records: unit tests PASS, Model Matrix Audit PASS, Python compile PASS, CLI smoke PASS, both Web UI JavaScript syntax checks PASS. These are **branch-reported results**, not a fresh test run performed by this documentation change.

Prior historical v0.2.0 post-merge CI/CodeQL evidence belongs to that earlier release; do not treat it as a v0.8.0 run.

## Next roadmap target

**v0.9 — Transport & Package Research Wave** (see [ROADMAP.md](ROADMAP.md)).

Prioritize exact package structure, event extraction and transport evidence for ROIDMI EVA/EVE, Xiaomi H40/M30/M40/X20+, Mijia 5/6, Viomi Alpha/V3, additional IJAI actions and modern Dreame. Do not promote build-only targets to installable without source-backed proof and exact-device verification.
