# Project status — v0.16.0 SOURCE SEALED (hardware acceptance pending)

- Canonical parent: **v0.15.0 SOURCE SEALED**, main SHA `4ba6bf234c66e55ab93571fd1a19cbc7ef456c35`.
- Source version: **0.16.0 — SOURCE SEALED** after exact-head CI, Public Site, Release Bundle, CodeQL, Desktop Packages macOS/Windows/Linux and merged-main verification.
- Functional release merged from [PR #32](https://github.com/aitishnyk/vacuum-voice-hub/pull/32) at `ba5d1bb1a4f89b9e4250f9e4df3091752658fd3c`; **canonical corrected source** now includes [PR #35](https://github.com/aitishnyk/vacuum-voice-hub/pull/35) (empty-first-recording review) at `3c27c9fcc53e0f524569b985ccd9f137e3254d23`.
- Models **215**, original credited voice variants **55**, built-in text-only locale scripts **18**. Matrix **11,825 software research combinations**, not 11,825 verified custom installs.
- v0.16 adds `vvh.production-review.v1` local per-model recording assignments (whole conservative event profile), English reference text explicitly not translated when missing and optional translated-text overlay.
- SHA-256 snapshots of Creator manifest plus individual assigned recordings; human recording review state machine `draft → recorded → listened → approved`, reviewer identity, time and two explicit human attestations. SHA drift invalidates a review; refresh preserves unchanged tasks and resets changed tasks to draft.
- Metadata-only review ZIP default, optional locally included raw audio with max 100 MiB cap, SHA-256 verification, new-path-only export and source privacy safeguards.
- Creator Studio panel and authenticated localhost endpoints for review creation/list/audit/refresh/mark/bundle; CLI exposes all workflows.
- Automated analysis **does not independently verify** real spoken language, identity of the person typing a reviewer name, copyright permissions or legal sufficiency. Human declarations are not cryptographically signed.
- No newly verified custom-install robot transport; Xiaomi X10 (`dreame.vacuum.r2209`) remains the only physically VVH-verified target. All other signed-only/build-only restrictions preserved.

## Preservation / exact-source release acceptance

Historical 109-model and 154-model ID/alias fixtures and all 215 current canonical model profiles retained. Voice catalog still has all 55 original attributed recordings and 18 text-only script locales. No new proprietary vendor transports or signed-pack bypass.

PR #32 final functional head `c2afa46e50a120fec603064556546c5ae7b5ccf0`:
- Python CI `37920118918`: **SUCCESS, 193/193 tests passed** (2 inherited third-party warnings).
- Second CI `37920112372`: SUCCESS.
- Model Matrix: **215 × 55 = 11,825** research-only software combinations, PASS.
- Public Site `37920118904`: SUCCESS.
- Release Bundle `37920118957`: SUCCESS.
- Desktop Packages `37920118955`: **SUCCESS on macOS, Windows and Linux**.
- PR CodeQL `37920113856`: SUCCESS.

Functional merged-main exact SHA `ba5d1bb1a4f89b9e4250f9e4df3091752658fd3c`:
- CI `37920419931`: SUCCESS.
- Public Site `37920419925`: SUCCESS.
- CodeQL Python and GitHub Actions `37920418786`: SUCCESS.
- Dependency graph `37920425038`: SUCCESS.

**SOURCE SEALED** means source tests and packaging gates passed; these review records are editable human attestations, not cryptographically signed identity evidence, independently established licenses or native-speaker certification. Real hardware installation and rollback evidence is still tracked in [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

## Corrective v0.16 release gate — zero-recording checklist

The original `v0.16` source gate was enhanced with PR #35: a brand-new Creator workspace with no audio now accepts a model-specific recording checklist while normal Creator pack builds still reject zero-audio packages. This is additive, with no new model IDs, voice entries, locale templates, dependencies or manufacturer install permissions.

PR #35 functional head `d579b9e144c6102f771dca0977904495c1609a9b`:
- CI `37920932623`: **SUCCESS, 194/194 tests passed**, 2 inherited warnings.
- Parallel CI `37920906046`: SUCCESS.
- Model Matrix: **215 × 55 = 11,825**, PASS.
- Public Site `37920932976`: SUCCESS.
- Release Bundle `37920932828`: SUCCESS.
- Desktop Packages `37920932905`: **SUCCESS macOS, Windows, Linux**.
- PR CodeQL `37920929470`: SUCCESS.

Merged-main corrected functional commit `3c27c9fcc53e0f524569b985ccd9f137e3254d23`:
- CI `37921176429`: SUCCESS.
- Public Site `37921176439`: SUCCESS.
- CodeQL Python + Actions `37921176647`: SUCCESS.

**Canonical v0.16.0 SOURCE SEALED = corrected main SHA `3c27c9fcc53e0f524569b985ccd9f137e3254d23`**, plus this status-only release-seal overlay. Physical device/firmware acceptance and standalone verification of human rights attestations remain explicitly unclaimed.

## Next priority

v0.17 — Voice QA Acceptance & Hardware Evidence, including reviewer-pack validation and device-specific verification; do not pretend the v0.16 software workflow unlocks manufacturer-signed voice transports.

See [v0.16 Production Review guide](docs/VOICE_PRODUCTION_REVIEW_V016.md).
