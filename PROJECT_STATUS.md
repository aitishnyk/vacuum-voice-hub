# Project status — v1.0.0 software-stable source candidate

**Release scope:** public, offline open-source **software** stable channel. This version number does not mean universal robot-voice installation capability.

- Base: v0.21.0 batch audio production built on v0.20.0 merged main `0fff08f51143ebed3cde1ea6b075aaeb3f06c232`. PR #47 source acceptance is tracked separately before this v1.0 branch can be merged.
- Includes 223 researched source-attributed model identities, 55 preserved attributed voice variants and 22 text-only locales; no new recorded voice language guarantees.
- Individual and folder-wide non-destructive offline audio mastering, QA signals, safe ZIP/TAR inspection, signed Ed25519 whole-pack provenance and Human Review workflows; no automatic upload to unknown robots.
- Source-revision audit `python scripts/stable_release_audit.py` must pass on **exact PR SHA**, alongside full Python suite, Model Matrix, public site/bundle, CodeQL and macOS/Windows/Linux desktop artifacts. Merged-main checks must independently pass after merge.
- **Hardware compatibility:** only Xiaomi X10 (`dreame.vacuum.r2209`) remains VVH physically verified. Unverified models are research/build-only or explicitly experimental/signed-only. Volunteers can submit exact model/firmware/rollback evidence; manufacturers/users may offer donations or loans without guaranteed endorsement or requiring us to own every robot.
- No commercial Telegram Stars/Bunny functionality in this public repository.
- This candidate is **NOT yet SOURCE SEALED**: acceptance results must be recorded before official stable status.

[Stable acceptance documentation](docs/STABLE_SOFTWARE_V100.md) · [Community device testing](docs/COMMUNITY_HARDWARE_TESTING.md).
