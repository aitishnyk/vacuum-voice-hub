# Project status — v0.14.0 SOFTWARE RELEASE CANDIDATE

- Canonical parent: **v0.13.0 SOURCE SEALED**, main SHA `8f2b6b251da26fac289fb97e3ea645da0385cc70`.
- New source version **0.14.0**; **CANDIDATE**, not source-sealed until exact-head CI / site / release / desktop checks pass.
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

## Acceptance required before SOURCE SEALED

Exact-head full Python test regression, matrix audit, source preservation, Release Bundle, Public Site, CodeQL and Windows/macOS/Linux desktop package builds. Verify merged `main` CI/CodeQL independently.

## Next priorities

- v0.15.0: deeper audio normalization / quality inspection for compressed sources and per-locale audio coverage.
- Real hardware download/apply/recovery for unverified robot families stays tracked separately in [#14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

See [v0.14 Creator Batch](docs/CREATOR_BATCH_V014.md).
