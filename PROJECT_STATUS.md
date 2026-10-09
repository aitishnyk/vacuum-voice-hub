# Project status — v0.14.0 SOURCE SEALED (hardware acceptance pending)

- Canonical parent: **v0.13.0 SOURCE SEALED**, main SHA `8f2b6b251da26fac289fb97e3ea645da0385cc70`.
- New source version **0.14.0 — SOURCE SEALED** after exact-head PR CI / site / release / three-OS desktop and merged-main CI/CodeQL.
- Functional merge: PR #26, commit `4cb669c65b8d09c7a65bda410962d3316d1e9fe7`.
- Model catalog: **215 unchanged**; source-attributed existing audio variants: **55 unchanged**; built-in text-only locales: **18 unchanged**.
- Existing model/voice software combination count remains **11,825**; this is software build/preview coverage, not hardware certification.
- New software: `vvh.creator-preflight.v1` per-model missing/core ID and collision audit with SHA-256 input integrity, optional WAV QA; `vvh.creator-batch.v1` multi-target offline package builder (1..16 models) with independent SHA-256 packages and no overwrites.
- Creator Studio localhost adds **Preflight** and **Build batch** UI controls, read-only report and authenticated batch API.
- Source voice licenses, third-party recorded audio redistribution and real hardware installation are never automatically authorized.

## Release safety and preservation

- All 215 existing canonical model IDs/aliases must remain preserved, including historical 109 + 154 baseline fixtures.
- All 55 credited catalog voices and 18 script locales must remain unchanged.
- New custom install transports: **0**; new hardware-verified target devices: **0**. Only **Xiaomi X10 (`dreame.vacuum.r2209`)** retains prior VVH hardware acceptance.
- New batch outputs for unsupported/signed-only models are reviewed offline and do **not** imply install compatibility. No robot connection is made by this workflow.
- Existing batch-output directories are refused, partial results cleaned, and changes to source audio during the build trigger failure.
- Unreviewed signal quality and legal redistribution remain outside automatic source gates.

## Verified release evidence

PR #26 final functional head `0ddac563035a3b9ed1a149054e6932f61e44ea0a`:
- Python CI `37912773995`: **SUCCESS**, 167 passed, 2 inherited third-party warnings.
- Parallel CI `37912738487`: SUCCESS.
- Model Matrix audit: **215 × 55 = 11,825** software combinations, original catalog identities retained.
- Public Site `37912773990`: SUCCESS.
- Release Bundle `37912774033`: SUCCESS.
- Desktop Packages `37912773962`: **SUCCESS on macOS, Windows and Linux**.
- PR CodeQL `37912770565`: SUCCESS.

Exact merged-main functional commit `4cb669c65b8d09c7a65bda410962d3316d1e9fe7`:
- CI `37913008136`: SUCCESS.
- Public Site `37913008148`: SUCCESS.
- CodeQL Python and GitHub Actions `37913007529`: SUCCESS.
- Dependency graph `37913012901`: SUCCESS.

**SOURCE SEALED** refers to software source/packaging only. It does not certify arbitrary robot voice uploads, code-sign/notarize binaries, validate voice redistribution rights or grant installation of research-only bundles.

## Next priorities

- v0.15.0: deeper audio normalization / quality inspection for compressed sources and per-locale audio coverage — [Issue #27](https://github.com/aitishnyk/vacuum-voice-hub/issues/27).
- Real hardware download/apply/recovery for unverified robot families stays tracked separately in [#14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

See [v0.14 Creator Batch](docs/CREATOR_BATCH_V014.md).
