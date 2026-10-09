# Project status — v0.18.0 SOURCE SEALED (hardware acceptance pending)

- Canonical parent: **v0.17.0 SOURCE SEALED**, main SHA `3e0b6124e2de14120158d3f279a1fb6338978942`.
- Source version **0.18.0 — SOURCE SEALED** after exact-head Python CI, model-matrix audit, PR CodeQL, Public Site, Release Bundle and three-OS Desktop Packages success, followed by independent merged-main CI and CodeQL.
- Functional [PR #40](https://github.com/aitishnyk/vacuum-voice-hub/pull/40) merged at exact SHA `d0a05c46d5476370eab59b5fbc1d79674a64cfb0`.
- Catalog preservation: **215** canonical profiles and aliases, **55** original attributed community voice variants and **18** built-in text script locales; software-only model/voice matrix **11,825** research combos.
- User-supplied local Ed25519 PEM key and detached signed `vvh.reviewer-attestation.v1` binds a currently approved human-reviewed recording to its exact audio SHA-256, locale, model, semantic/event IDs, translation digest, Creator manifest SHA, reviewer declaration and signed timestamp. Verification rechecks present audio and local review. Original audio and review never modified by signing.
- Optional `cryptography>=42` available as `review-signing` extra; CI/desktop build includes it. VVH never creates, stores or uploads a private signing key. A valid signature authenticates **key possession**, not a verified human identity, legal rights, actual spoken language or successful firmware upload.
- `vvh.review-audio-acceptance.v1` compares per-clip signal QA and human review status separately; opt-in compressed decoding, per-call maximum 32 clips, no implicit approval.
- Creator Studio adds the Audio & Human QA button and a 5-step model/firmware candidate package evidence panel. Even full reported signature/download/playback/reboot/rollback observations cannot alter an installer policy.
- Hardware: **only Xiaomi X10** (`dreame.vacuum.r2209`) retains previous VVH-tested custom voice installation evidence. New verified custom install transports = **0**, token/region workarounds = **0**.

## Preservation and exact-source release acceptance

Previous 215 model IDs and aliases, original 55 attributed voice variants, 18 text-script locales and historical 109/154 identity fixtures preserved. Voice install capability on unverified/signed manufacturer firmware has not been promoted.

PR #40 final functional SHA `7ef5c0fe6da6f87a66016026121084b689108d0f`:
- Python CI `37942969874`: **SUCCESS — 215 tests passed, 3 warnings**.
- Parallel CI `37942963387`: SUCCESS.
- Model Matrix: **215 × 55 = 11,825** research software-only combinations, PASS.
- Public Site `37942969795`: SUCCESS.
- Release Bundle `37942969661`: SUCCESS.
- Desktop Packages `37942969812`: **SUCCESS macOS, Windows, Linux**.
- PR CodeQL `37942965001`: SUCCESS.
- Linux GTK/WebKit apt setup has a finite timeout and bounded retries; all desktop artifacts were built and uploaded before functional merge.

Exact merged-main functional SHA `d0a05c46d5476370eab59b5fbc1d79674a64cfb0`:
- CI `37943289552`: SUCCESS.
- Public Site `37943289481`: SUCCESS.
- CodeQL Python and GitHub Actions `37943289496`: SUCCESS.
- Dependency graph `37943299509`: SUCCESS.

**SOURCE SEALED** is software source/packaging acceptance, not proof of manufacturer-signed firmware compatibility, physical robot playback, independent reviewer identity, recording copyright ownership, or correct spoken language. Optional cryptographic signing verifies user-supplied Ed25519 key possession and current reviewed-audio integrity only.

## Next priority

v0.19 ([Issue #41](https://github.com/aitishnyk/vacuum-voice-hub/issues/41)) — independent firmware playback/rollback acceptance tooling and safe release provenance for signed voice packages without weakening manufacturer restrictions. Physical evidence: [#14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

Guide: [v0.18 reviewer provenance and audio QA](docs/REVIEWER_PROVENANCE_V018.md).
