# Project status — v0.19.0 SOFTWARE RELEASE CANDIDATE

- Canonical parent: **v0.18.0 SOURCE SEALED**, main SHA `8952026aea73357723b988b31e23401fed1c5cd1`.
- Version **0.19.0 CANDIDATE** pending exact PR-head full regression, 215×55 model-matrix, Public Site, Release Bundle, PR CodeQL and macOS/Windows/Linux Desktop Packages plus independent merged-main checks.
- Whole-pack `vvh.signed-pack-manifest.v1` signs the specific 215-model-compatible selected Creator review's **assigned** audio SHA-256/byte lengths, semantic/event IDs, selected text script, source manifest SHA, explicit per-clip human review and locale using a **user-supplied local Ed25519 PEM key**. `--require-approved` refuses any assigned audio without local human approval. Verification reopens original local audio/review; it is not a certified audio distributor.
- Hardware evidence `vvh.firmware-evidence-bundle.v1`: locally hash-checks candidate package before creating or verifying a metadata-only evidence ZIP with exact canonical model ID, firmware, package digest/size and five self-reported observation flags. It **never copies or uploads actual firmware, passwords, token or installer data**. Complete self-report yields only independent-review readiness, never custom-install permission.
- Preservation: **215 canonical models**, **55 attributed source voice variants**, **18 built-in text-only scripts**, historic 109/154 model fixtures unchanged. **Xiaomi X10 `dreame.vacuum.r2209` remains the only physically verified VVH custom voice install target**. All other models retain previous research/build-only or unsupported transport policy.
- User Ed25519 signatures prove **possession of a key**, not real-world reviewer identity, legal audio redistribution rights or spoken-language accuracy. Physical compatibility needs specific version/device playback, persistence and working stock rollback independent verification [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

## Source acceptance required

No SOURCE SEALED, live install claim, or final release status before **all** full tests, static site, release ZIP, CodeQL, model audit and three-OS desktop artifacts pass exact functional PR head, followed by merged-main CI/CodeQL.

Guide: [v0.19 signed whole pack and hardware evidence](docs/SIGNED_PACK_EVIDENCE_V019.md).

## Next version

v0.20 — independent hardware acceptance and user-facing signature verification plus expanded Creator reviewer workflows. Real on-device custom install verification requires external proof and remains open independently.
