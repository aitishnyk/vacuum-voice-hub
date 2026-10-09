# Project status — v0.16.0 SOFTWARE RELEASE CANDIDATE

- Canonical parent: **v0.15.0 SOURCE SEALED**, main SHA `4ba6bf234c66e55ab93571fd1a19cbc7ef456c35`.
- Source version: **0.16.0**. Release candidate until exact-head CI, Public Site, Release Bundle, CodeQL, Desktop Packages macOS/Windows/Linux and merged-main verification are green.
- Models **215**, original credited voice variants **55**, built-in text-only locale scripts **18**. Matrix **11,825 software research combinations**, not 11,825 verified custom installs.
- v0.16 adds `vvh.production-review.v1` local per-model recording assignments (whole conservative event profile), English reference text explicitly not translated when missing and optional translated-text overlay.
- SHA-256 snapshots of Creator manifest plus individual assigned recordings; human recording review state machine `draft → recorded → listened → approved`, reviewer identity, time and two explicit human attestations. SHA drift invalidates a review; refresh preserves unchanged tasks and resets changed tasks to draft.
- Metadata-only review ZIP default, optional locally included raw audio with max 100 MiB cap, SHA-256 verification, new-path-only export and source privacy safeguards.
- Creator Studio panel and authenticated localhost endpoints for review creation/list/audit/refresh/mark/bundle; CLI exposes all workflows.
- Automated analysis **does not independently verify** real spoken language, identity of the person typing a reviewer name, copyright permissions or legal sufficiency. Human declarations are not cryptographically signed.
- No newly verified custom-install robot transport; Xiaomi X10 (`dreame.vacuum.r2209`) remains the only physically VVH-verified target. All other signed-only/build-only restrictions preserved.

## Preservation / acceptance

All 215 previous canonical model IDs, alias owners and adapters are preserved; historic 109/154 fixtures unchanged. 55 attributed community audio variants and 18 original locale scripts unchanged. Source-seal requires 100% functional regression, model matrix, CodeQL, site/release packaging and all three desktop OS build jobs. Real hardware/firmware acceptance and rollback remain separately tracked in [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

## Next priority

v0.17 — Voice QA Acceptance & Hardware Evidence, including reviewer-pack validation and device-specific verification; do not pretend the v0.16 software workflow unlocks manufacturer-signed voice transports.

See [v0.16 Production Review guide](docs/VOICE_PRODUCTION_REVIEW_V016.md).
