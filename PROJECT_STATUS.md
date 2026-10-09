# Project status — v0.17.0 SOURCE SEALED (hardware acceptance pending)

- Canonical parent: v0.16.0 SOURCE SEALED, main SHA `11817097466dba6b9a02228520171097df799c6a`.
- Source version **0.17.0 — SOURCE SEALED** after exact-head Python CI, CodeQL, Public Site, Release Bundle and macOS/Windows/Linux desktop builds PASS, plus merged-main repeat.
- Functional release [PR #37](https://github.com/aitishnyk/vacuum-voice-hub/pull/37) merged at `db78db3979242707dd7cabe52fc7201d42f9a06a`.
- Model profiles **215**, original source-backed voice variants **55**, built-in text-only script locales **18**, research software coverage **11,825 model × voice variants**. Nothing in v0.17 installs new unsigned packages or verifies additional physical robots.
- Added a returned reviewer JSON/ZIP safe importer: ZIP is validated in memory, **never extracted**, content and local Creator manifest/semantic/text/model/audio SHA-256 fingerprints must agree. Remote approvals stored as **untrusted external claims**, local review status starts draft; no local approvals transferred.
- Added hash-linked local review history for mark, refresh and imported claims, with pre-edit journal checks. Hash chain is not cryptographically authenticated and can be deliberately rewritten by someone with full filesystem access.
- Added local `vvh.hardware-acceptance.v1` model+firmware+package evidence checklist for signature claims, download, audible playback, reboot persistence and rollback. Even complete observed flags only yield `ready-for-independent-hardware-review`, never a transport policy change.
- Creator Studio can import only small metadata handoff JSON/ZIP (up to 2 MiB), plus inspect history; CLI accepts bounded 105 MiB ZIP for explicitly included original recordings.
- No live vendor API actions, model registry mutations, new robot transport grants or audio redistribution certification. Xiaomi X10 (`dreame.vacuum.r2209`) remains the VVH hardware-verified installation target.

## Preservation and exact-source release acceptance

All 215 prior model identities and aliases preserved, original 55 attributed voice variants and 18 built-in locale scripts unchanged; historic 109/154 model identity fixtures remain protected. No new device firmware bypass or custom-install authorization.

PR #37 final functional SHA `6f35cb8e6b5aee7b1f1ce4f06953da442ffec41d`:
- CI run `37928611302`: **SUCCESS, 207/207 tests passed** (3 warnings, including an intentional duplicate-ZIP-entry negative fixture).
- Second CI run `37928605289`: SUCCESS.
- Model Matrix: **215 × 55 = 11,825** software research-only target combinations, PASS.
- Public Site run `37928611277`: SUCCESS.
- Release Bundle run `37928611362`: SUCCESS.
- Desktop Packages run `37928611339`: **SUCCESS for macOS, Windows and Linux**.
- PR CodeQL run `37928607478`: SUCCESS.

Merged-main exact functional SHA `db78db3979242707dd7cabe52fc7201d42f9a06a`:
- CI run `37928863316`: SUCCESS.
- Public Site `37928863408`: SUCCESS.
- CodeQL Python/Actions `37928862997`: SUCCESS.
- Dependency graph `37928869137`: SUCCESS.

**SOURCE SEALED** means these software and packaging gates passed, NOT that any imported reviewer identity, recording rights, licensing, native pronunciation or vendor-signed custom install is independently verified. Reported playback/reboot/stock-rollback evidence remains research-only and never changes install policy. Physical verification remains [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

## Future work

v0.18 ([Issue #38](https://github.com/aitishnyk/vacuum-voice-hub/issues/38)): explicit independently verifiable signing of reviewer decisions, comparison of listening QA/recording quality against user-supplied samples, and further real-hardware firmware package research. Real physical installation proof tracked by [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

Guide: [v0.17 Returned Reviewer Handoff & Evidence](docs/REVIEW_HANDOFF_V017.md).
