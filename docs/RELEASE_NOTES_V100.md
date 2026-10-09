# Vacuum Voice Hub v1.0.0 — Software Stable

This is a stable **offline open-source software core** release, not an official
endorsement or a promise of custom voice installation on every vacuum robot.

## Included

- **223** source-attributed robot model/research profiles (without inventing installability).
- **55** preserved, credited voice variants in the source catalog.
- **22** text-only translated reference script languages, each with 16 core events. Newly translated locales still need native-speaker review; not prerecorded libraries.
- Creator Studio, local optional TTS engines, per-model compatibility/preflight/semantic bundle tools and audio QA.
- **Individual and batch mastering** of local recordings: silence trimming, padding, fades, guarded peak normalization, new-file-only WAV output, per-clip SHA-256 and all-or-nothing batch rollback.
- Human Review, Ed25519 whole-pack provenance and firmware metadata-only evidence workflow.
- Machine-readable stable source audit, legacy model/alias preservation and GitHub CI / CodeQL / desktop build validation.

## Compatibility remains evidence-scoped

**Only Xiaomi X10 (`dreame.vacuum.r2209`) has VVH physically verified custom-install support.** Other models retain separate build/research/experimental/signed-only policies. A successful software package build does not prove that any specific firmware accepts it.

Community members can submit redacted exact model/firmware/audio playback/reboot/stock rollback evidence. Manufacturers or users can voluntarily loan or donate robots without influencing evaluation or guaranteeing support. See `docs/COMMUNITY_HARDWARE_TESTING.md`.

## Artifacts and distribution rights

The release assets contain a public metadata/catalog ZIP, deterministic
release manifest, update feed, SHA256SUMS and software bill of materials.
GitHub automatically provides tagged source code archives.

**No copyrighted third-party voice recordings, proprietary firmware,
robot tokens or Wi-Fi credentials are included.** The catalog and signatures
do not confer redistribution rights for upstream recordings.

Desktop executables were verified for macOS/Windows/Linux in exact PR-head CI,
but this automated publication **does not attach signed/notarized desktop
installers**. See GitHub Actions artifacts for test builds, and review their
provenance before use.

For full software acceptance and evidence, read `docs/STABLE_SOFTWARE_V100.md`.
