# Project status — v0.15.0 SOFTWARE RELEASE CANDIDATE

- Canonical parent: v0.14.0 SOURCE SEALED, main SHA `44709991258594c8f33046f70855da00e2edf672`.
- Source version **0.15.0**, not sealed until exact-head CI, Public Site, Release Bundle, CodeQL and macOS/Windows/Linux Desktop Packages succeed.
- Existing canonical models: **215**, attributed community audio variants: **55**, built-in *text-only* script locales: **18**. Matrix: **11,825 software targets**; no new robot install authority.
- Added bounded opt-in local FFmpeg analysis of MP3, OGG, FLAC, M4A, AAC and Opus; existing WAV QC preserved.
- Added non-destructive gain-only preview WAV with before/after signal QA, exclusive new path and SHA-256; never edits source audio/Creator manifest.
- Added per-model text-versus-audio localization coverage with mismatched-locale safeguards; metadata alone never proves voice speech language or license ownership.
- Creator Studio adds compressed-source QA opt-in and Text vs Audio Coverage; CLI and local read-only API added.
- Compressed media decoder caps local input and decoded output and enforces timeout and FFmpeg local-only allowed protocols.

## Preservation / limitations

- All historical 109-model and 154-model baselines remain intact; current 215-model catalog/aliases and all 55 voice entries unchanged.
- Xiaomi X10 (`dreame.vacuum.r2209`) remains **the only physically verified VVH target**. No new vendor-signed bypass or custom-install claims, firmware patches or region unlocks.
- Signal QC, TTS, model ID discovery and locale script counts do **not** prove actual installed custom voice functionality. Audio rights and native-speaker accuracy require human acceptance.
- No new mandatory runtime dependency: v0.15 reuses the previously bundled/runtime FFmpeg.
- See [v0.15 audio guide](docs/COMPRESSED_AUDIO_QA_V015.md).

## Source acceptance

Requires exact PR head: full Python regression, model-matrix audit, Release Bundle, Public Site, CodeQL and all three desktop package jobs. For source sealing additionally verify merged-main CI/Public Site/CodeQL and record the corresponding run IDs.

## Next wave

v0.16 Voice Production Workflow & Safety Evidence — additional local voice review and quality gates while preserving immutable original model/voice catalog identities; real hardware acceptance tracked separately in [#14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).
