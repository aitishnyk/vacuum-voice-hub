# Project status — v0.13.0 SOURCE SEALED (hardware acceptance pending)

- Canonical starting point: v0.12.0 SOURCE SEALED, main SHA `250b834ef15a99a47a407d03725826def491e990`.
- Source version: **0.13.0**, **SOURCE SEALED** after exact-head CI, Release Bundle, Public Site, three-OS Desktop Packages and merged-main CodeQL.
- Functional v0.13 merge SHA: `7f5f819a2a28c925375c0b13a7a8e525aac0e938` (PR #23).
- Canonical models: **215** = unchanged original 154 + 61 newly source-listed MIoT identities.
- Existing source-attributed audio voice variants: **55**, unchanged; built-in text-only locale scripts: **18**, unchanged.
- Software coverage matrix: **215 × 55 = 11,825 combinations**, not 11,825 physically working custom voice installations.
- Additions: **26 Viomi**, **19 Xiaomi/Mijia**, **9 Roborock**, **4 ROIDMI**, **3 IJAI**.
- All added devices are portable `semantic_bundle` research profiles with `unsupported-local` fail-closed transport; no new `device_tested` hardware flags.
- Xiaomi X10 (`dreame.vacuum.r2209`) remains the **only** physically tested VVH installation target.
- `model-compare` displays overlapping event IDs / package research hints, **never** authorizes custom package installation.
- Public model catalog adds links to MIoT identity sources for new devices; no new firmware/package acceptance claims.

## Preservation / exact-source verification

- Historical 109 canonical models pinned in `tests/fixtures/v08_model_identity.json` and historical 154 canonical models in `tests/fixtures/v012_model_identity.json`. All original IDs, aliases, adapters and transport policies preserved.
- Packaged `vacuum_voice_hub/data/models.json` remains byte-identical to `catalog/models.json`.
- 55 attributed audio voices and 18 core text-only locales preserved; no new third-party audio or unsigned binary claimed.

PR #23 head `b916a6566db92647833c9640b1668a8222652a3b`:
- Python CI run `37910777718`: **SUCCESS — 157 passed, 2 inherited python-miio deprecation warnings**.
- Model Matrix: **215 × 55 = 11,825** software combinations PASS.
- PR CodeQL `37910773688`: SUCCESS.
- Public Site `37910777726`: SUCCESS.
- Release Bundle `37910777751`: SUCCESS.
- Desktop Packages `37910777959`: SUCCESS, macOS / Windows / Linux.

On exact merged-main SHA `7f5f819a2a28c925375c0b13a7a8e525aac0e938`:
- CI run `37911043239`: SUCCESS.
- Public Site `37911043260`: SUCCESS.
- CodeQL Python + GitHub Actions `37911042252`: SUCCESS.
- Dependency graph `37911050236`: SUCCESS.

Source sign-off does **not** assert manufacturer custom voice installation on newly added devices, spoken-language review, trusted voice license grants, code signing or notarization of binaries.

## Unverified hardware

Modern Xiaomi H40/H50/X20/S40, Viomi, ROIDMI, IJAI and Roborock Qrevo installations remain unverified. Per-device+firmware custom package and transport/recovery acceptance is tracked in [Hardware Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14). A MIoT device listing or model action-control support cannot certify an arbitrary custom voice pack.

## Roadmap

v0.14 candidate priority: Audio & Voice Pack Adaptation QA; subsequent evidence-backed package adapters. See [multibrand device research](docs/MULTIBRAND_DISCOVERY_V013.md).
