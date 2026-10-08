# Project status — v0.9.1 (software release candidate)

- Product: **Vacuum Voice Hub**
- Repository: `aitishnyk/vacuum-voice-hub`
- Source version: **0.9.1** (security update after v0.9.0)
- Verified v0.9.0 merge on `main`: `11f5220d3ed3009fc3643767a4c53aac28ec6a94` (PR #12)
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

## Verification gates

Merged PR #12 `v0.9.0` passed GitHub CI, Release Bundle, Public Site and desktop packaging checks. This v0.9.1 archive-extraction security update must pass its **own** exact-head tests before merge. No physical acceptance test on a new robot is claimed by CI.

## Open v1.0 hardware tasks

Obtain exact-device, consented package and transport evidence for ROIDMI EVA/EVE, Xiaomi H40/M30/M40/X20+, Mijia 5/6, Viomi Alpha/V3 and modern Dreame. Add exact adapter and real-device tests only after proof. These remain **not completed** by v0.9.1 software delivery; see [ROADMAP.md](ROADMAP.md).
