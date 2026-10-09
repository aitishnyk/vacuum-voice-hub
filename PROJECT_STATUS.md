# Project status — v0.13.0 SOFTWARE RELEASE CANDIDATE

- Canonical starting point: v0.12.0 SOURCE SEALED, main SHA `250b834ef15a99a47a407d03725826def491e990`.
- Source version: **0.13.0**, candidate until exact-head GitHub CI, release bundle, public site and desktop package tests succeed.
- Canonical models: **215** = unchanged original 154 + 61 newly source-listed MIoT identities.
- Existing source-attributed audio voice variants: **55**, unchanged; built-in text-only locale scripts: **18**, unchanged.
- Software coverage matrix: **215 × 55 = 11,825 combinations**, not 11,825 physically working custom voice installations.
- Additions: **26 Viomi**, **19 Xiaomi/Mijia**, **9 Roborock**, **4 ROIDMI**, **3 IJAI**.
- All added devices are portable `semantic_bundle` research profiles with `unsupported-local` fail-closed transport; no new `device_tested` hardware flags.
- Xiaomi X10 (`dreame.vacuum.r2209`) remains the **only** physically tested VVH installation target.
- `model-compare` displays overlapping event IDs / package research hints, **never** authorizes custom package installation.
- Public model catalog adds links to MIoT identity sources for new devices; no new firmware/package acceptance claims.

## Preservation / acceptance

- Old 109-model baseline from `tests/fixtures/v08_model_identity.json` must remain unchanged.
- Additional previous 154-model baseline from `tests/fixtures/v012_model_identity.json` protects all canonical IDs, aliases, adapters, transports and hardware-test status.
- Original `catalog/models.json` and packaged `vacuum_voice_hub/data/models.json` must remain byte-identical after the 61-entry cumulative merge.
- 55 attributed voices are preserved; no unlicensed new audio assets added; translation overlays and Piper/eSpeak remain user-run local workflows.
- CI, model matrix audit, public site, release bundle, macOS/Linux/Windows desktop packaging must all PASS before source sealing.

## Unverified hardware

Modern Xiaomi H40/H50/X20/S40, Viomi, ROIDMI, IJAI and Roborock Qrevo installations remain unverified. Per-device+firmware custom package and transport/recovery acceptance is tracked in [Hardware Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14). A MIoT device listing or model action-control support cannot certify an arbitrary custom voice pack.

## Roadmap

v0.14 candidate priority: Audio & Voice Pack Adaptation QA; subsequent evidence-backed package adapters. See [multibrand device research](docs/MULTIBRAND_DISCOVERY_V013.md).
