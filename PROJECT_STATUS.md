# Project status — v0.15.0 SOURCE SEALED (hardware acceptance pending)

- Canonical parent: v0.14.0 SOURCE SEALED, main SHA `44709991258594c8f33046f70855da00e2edf672`.
- Source version **0.15.0 — SOURCE SEALED** after exact-head CI, Public Site, Release Bundle, PR CodeQL and three-OS Desktop Packages, with merged-main verification.
- Functional merge PR #29: `bc7734034bfecff50fd2474e6e19277cecf00e9d`.
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

## Exact-source release acceptance

PR #29 final head `4d581c115810e6850ad6489b89f132a23da5de69`:
- CI run `37915047751`: **SUCCESS, 178/178 tests passed**, 2 inherited third-party deprecation warnings.
- Parallel CI run `37915041124`: SUCCESS.
- Model Matrix: **215 models × 55 voices = 11,825** software-only combinations, PASS.
- Public Site `37915047689`: SUCCESS.
- Release Bundle `37915047644`: SUCCESS.
- Desktop Packages `37915047730`: **SUCCESS for macOS, Windows and Linux**.
- PR CodeQL `37915041829`: SUCCESS.

Exact functional merged-main commit `bc7734034bfecff50fd2474e6e19277cecf00e9d`:
- CI `37915322086`: SUCCESS.
- Public Site `37915321993`: SUCCESS.
- CodeQL Python and GitHub Actions `37915321636`: SUCCESS.
- Dependency graph `37915326228`: SUCCESS.

**SOURCE SEALED** is software source/packaging acceptance, not manufacturer custom voice installation approval or native-speaker/licensing certification. Signal QC uses temporary decoded audio and never changes the original recording without an explicit separate operation.

## Next wave

v0.16 Voice Production Workflow & Safety Evidence ([Issue #30](https://github.com/aitishnyk/vacuum-voice-hub/issues/30)) — additional local voice review and quality gates while preserving immutable original model/voice catalog identities; real hardware acceptance tracked separately in [#14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).
