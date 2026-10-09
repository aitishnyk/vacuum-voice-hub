# Project status — v0.18.0 SOFTWARE RELEASE CANDIDATE

- Canonical parent: **v0.17.0 SOURCE SEALED**, main SHA `3e0b6124e2de14120158d3f279a1fb6338978942`.
- Source version **0.18.0**. **CANDIDATE**, not sealed until exact-head Python tests, source matrix, CodeQL, Public Site, Release Bundle and Desktop Packages macOS/Windows/Linux pass; recheck merged-main CI/CodeQL.
- Catalog preservation: **215** canonical profiles and aliases, **55** original attributed community voice variants and **18** built-in text script locales; software-only model/voice matrix **11,825** research combos.
- User-supplied local Ed25519 PEM key and detached signed `vvh.reviewer-attestation.v1` binds a currently approved human-reviewed recording to its exact audio SHA-256, locale, model, semantic/event IDs, translation digest, Creator manifest SHA, reviewer declaration and signed timestamp. Verification rechecks present audio and local review. Original audio and review never modified by signing.
- Optional `cryptography>=42` available as `review-signing` extra; CI/desktop build includes it. VVH never creates, stores or uploads a private signing key. A valid signature authenticates **key possession**, not a verified human identity, legal rights, actual spoken language or successful firmware upload.
- `vvh.review-audio-acceptance.v1` compares per-clip signal QA and human review status separately; opt-in compressed decoding, per-call maximum 32 clips, no implicit approval.
- Creator Studio adds the Audio & Human QA button and a 5-step model/firmware candidate package evidence panel. Even full reported signature/download/playback/reboot/rollback observations cannot alter an installer policy.
- Hardware: **only Xiaomi X10** (`dreame.vacuum.r2209`) retains previous VVH-tested custom voice installation evidence. New verified custom install transports = **0**, token/region workarounds = **0**.

## Required source acceptance

Exact PR head and merged-main full regression, 215×55 model matrix, Public Site/Release Bundle, three desktop systems and CodeQL. Do not seal or claim hardware readiness until these gates pass.

## Next priority

v0.19 — independent firmware playback/rollback acceptance tooling and safe release provenance for signed voice packages without weakening manufacturer restrictions. Physical evidence: [#14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

Guide: [v0.18 reviewer provenance and audio QA](docs/REVIEWER_PROVENANCE_V018.md).
