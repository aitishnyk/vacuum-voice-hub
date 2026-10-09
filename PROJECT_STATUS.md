# Project status — v0.19.0 SOURCE SEALED (hardware acceptance pending)

- Canonical parent: **v0.18.0 SOURCE SEALED**, main SHA `8952026aea73357723b988b31e23401fed1c5cd1`.
- Version **0.19.0 — SOURCE SEALED** after exact PR-head full regression, model matrix, Public Site, Release Bundle, PR CodeQL and three-OS Desktop Packages, followed by independent merged-main CI/CodeQL.
- Functional [PR #43](https://github.com/aitishnyk/vacuum-voice-hub/pull/43) merged as `13ee31da554cc3d3fc1f458a57e0f156c624925b`.
- Whole-pack `vvh.signed-pack-manifest.v1` signs the specific 215-model-compatible selected Creator review's **assigned** audio SHA-256/byte lengths, semantic/event IDs, selected text script, source manifest SHA, explicit per-clip human review and locale using a **user-supplied local Ed25519 PEM key**. `--require-approved` refuses any assigned audio without local human approval. Verification reopens original local audio/review; it is not a certified audio distributor.
- Hardware evidence `vvh.firmware-evidence-bundle.v1`: locally hash-checks candidate package before creating or verifying a metadata-only evidence ZIP with exact canonical model ID, firmware, package digest/size and five self-reported observation flags. It **never copies or uploads actual firmware, passwords, token or installer data**. Complete self-report yields only independent-review readiness, never custom-install permission.
- Preservation: **215 canonical models**, **55 attributed source voice variants**, **18 built-in text-only scripts**, historic 109/154 model fixtures unchanged. **Xiaomi X10 `dreame.vacuum.r2209` remains the only physically verified VVH custom voice install target**. All other models retain previous research/build-only or unsupported transport policy.
- User Ed25519 signatures prove **possession of a key**, not real-world reviewer identity, legal audio redistribution rights or spoken-language accuracy. Physical compatibility needs specific version/device playback, persistence and working stock rollback independent verification [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

## Exact-source release acceptance and preservation

Feature PR #43 final functional head `5bb262d5c4b7ccced758fc42f2f54f0d4a6e3c41`:
- Python CI `37950646205`: **SUCCESS — 224 tests passed**, 3 inherited warnings.
- Second CI `37950636296`: SUCCESS.
- Model Matrix audit: **215 × 55 = 11,825** research software-only model+voice combinations, PASS; historical 109/154 identity fixtures preserved.
- Public Site `37950646323`: SUCCESS.
- Release Bundle `37950646267`: SUCCESS.
- Desktop Packages `37950646271`: **SUCCESS macOS, Windows, Linux**.
- PR CodeQL `37950640447`: SUCCESS.

Exact functional merged-main commit `13ee31da554cc3d3fc1f458a57e0f156c624925b`:
- CI `37951122821`: SUCCESS.
- Public Site `37951122823`: SUCCESS.
- CodeQL Python+GitHub Actions `37951122338`: SUCCESS.
- Dependency Graph `37951135641`: SUCCESS.

**SOURCE SEALED** attests that software regression, static site and packaging gates pass. It does not establish physical custom-voice installation on any additional robot, native-language accuracy, licensing/redistribution rights or independent validity of self-reported manufacturer acceptance evidence. The firmware-evidence bundle contains metadata only; the actual package remains local to the verifier. Real device/firmware acceptance remains [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

Guide: [v0.19 signed whole pack and hardware evidence](docs/SIGNED_PACK_EVIDENCE_V019.md).

## Next version

v0.20 — independent hardware acceptance and user-facing signature verification plus expanded Creator reviewer workflows. Real on-device custom install verification requires external proof and remains open independently.
