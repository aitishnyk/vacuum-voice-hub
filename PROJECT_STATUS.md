# Project status — v0.9.1 SOURCE SEALED (hardware acceptance pending)

- Product: **Vacuum Voice Hub**
- Repository: `aitishnyk/vacuum-voice-hub`
- Source version: **0.9.1** (security update after v0.9.0)
- v0.9.0 functional merge: `11f5220d3ed3009fc3643767a4c53aac28ec6a94` (PR #12)
- v0.9.1 security merge: `03ac57515e5a28cdca626f043ab3332449b07cc2` (PR #13)
- Source release state: **SEALED / CI-confirmed**. Hardware-wide production acceptance: **NOT COMPLETE**.
- Model profiles: **109**; source-attributed voice variants: **55**.
- Software compatibility matrix: **5,995 voice × model combinations**, not 5,995 verified physical installations.
- Target adapters: 32 Dreame numeric, 33 classic Roborock, 8 IJAI, 36 semantic/build-only.
- Physically verified VVH target: **Xiaomi X10 (`dreame.vacuum.r2209`) only**.
- Community audio variants are source-attributed/conversion-ready, not automatically hardware-certified.

## Software capabilities

- Model-aware compatibility, fallback, semantic event filtering and audio preview.
- Model-specific output: Dreame OGG/TAR.GZ, legacy Roborock WAV/PKG, IJAI named MP3/ZIP, portable research-only bundles.
- Creator Studio, CLI, desktop shells, local Web UI and searchable public catalog.
- Privacy-safe history and `vvh.compat-report.v1`.
- Reproducible public-site/release bundle, SPDX SBOM and SHA256SUMS.
- v0.9: local `vvh research inspect` and `vvh research validate-evidence`, bounded metadata inventory, source-report SHA-256 and exact-model verification, numerical event-profile cross-check, three published JSON schemas.
- v0.9.1: bounded ZIP/TAR import extraction, pre-write path and duplicate checks, special-file/link rejection and resource limits on Python 3.10+.

## Installation and acceptance boundaries

- X10: previously hardware-verified local transport, individual catalog packs require their own device validation.
- Classic Roborock local and known IJAI pathways: explicit experimental opt-in only.
- Vendor-signed new Roborock: arbitrary custom packs blocked.
- Other unknown Xiaomi/Mijia/Viomi/ROIDMI/Smartmi transport: build, preview, compatibility and research only.
- Research evidence and `hardware-review-required` reports can never authorize installation or mutate the model registry.
- Binaries are not considered signed/notarized without actual signing evidence.

## Verification gates (exact main commit)

GitHub Actions on v0.9.1 merged main commit `03ac57515e5a28cdca626f043ab3332449b07cc2`:

- CI run `37851383867`: **SUCCESS**.
- Public Site run `37851383835`: **SUCCESS**.
- CodeQL (Python + Actions) / Push on main run `37851383586`: **SUCCESS**.
- Dependency graph run `37851390939`: **SUCCESS**.

PR #13 exact-head gates before merge:

- CI `37851147846`: **SUCCESS**.
- PR checks `37851142975`: **SUCCESS**.
- Release Bundle `37851147854`: **SUCCESS**.
- Public Site `37851147818`: **SUCCESS**.
- Desktop Packages `37851147885`: **SUCCESS** for macOS, Linux and Windows.

These are source-build and packaging results; real-device acceptance of new models and signed/notarized distributables remain separate evidence requirements.

## Open v1.0 hardware tasks

Obtain exact-device, consented package and transport evidence for ROIDMI EVA/EVE, Xiaomi H40/M30/M40/X20+, Mijia 5/6, Viomi Alpha/V3 and modern Dreame. Add exact adapter and real-device tests only after proof. These remain **not completed** by v0.9.1 software delivery; see [ROADMAP.md](ROADMAP.md) and [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).
