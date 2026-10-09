# Project status — v0.17.0 SOFTWARE RELEASE CANDIDATE

- Canonical parent: v0.16.0 SOURCE SEALED, main SHA `11817097466dba6b9a02228520171097df799c6a`.
- Source version **0.17.0**, candidate until exact-head CI, CodeQL, Public Site, Release Bundle and macOS/Windows/Linux desktop gates PASS; merged-main verification required.
- Model profiles **215**, original source-backed voice variants **55**, built-in text-only script locales **18**, research software coverage **11,825 model × voice variants**. Nothing in v0.17 installs new unsigned packages or verifies additional physical robots.
- Added a returned reviewer JSON/ZIP safe importer: ZIP is validated in memory, **never extracted**, content and local Creator manifest/semantic/text/model/audio SHA-256 fingerprints must agree. Remote approvals stored as **untrusted external claims**, local review status starts draft; no local approvals transferred.
- Added hash-linked local review history for mark, refresh and imported claims, with pre-edit journal checks. Hash chain is not cryptographically authenticated and can be deliberately rewritten by someone with full filesystem access.
- Added local `vvh.hardware-acceptance.v1` model+firmware+package evidence checklist for signature claims, download, audible playback, reboot persistence and rollback. Even complete observed flags only yield `ready-for-independent-hardware-review`, never a transport policy change.
- Creator Studio can import only small metadata handoff JSON/ZIP (up to 2 MiB), plus inspect history; CLI accepts bounded 105 MiB ZIP for explicitly included original recordings.
- No live vendor API actions, model registry mutations, new robot transport grants or audio redistribution certification. Xiaomi X10 (`dreame.vacuum.r2209`) remains the VVH hardware-verified installation target.

## Preservation and release gates

All 215 former canonical IDs/aliases, original 55 community source voice variants, 18 text scripts and 109/154 model snapshots must remain unchanged. Automated Python tests must include positive JSON/ZIP roundtrips plus negative traversal, duplicate, altered audio, stale workspace, corrupted history and forged model/firmware evidence checks.

Full acceptance: CI regression, model matrix, Public Site, Release Bundle, CodeQL PR and exact-main repeat, desktop packages macOS/Windows/Linux. Do not call source SEALED until those gates are complete.

## Future work

v0.18: explicit independently verifiable signing of reviewer decisions, comparison of listening QA/recording quality against user-supplied samples, and further real-hardware firmware package research. Real physical installation proof tracked by [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

Guide: [v0.17 Returned Reviewer Handoff & Evidence](docs/REVIEW_HANDOFF_V017.md).
