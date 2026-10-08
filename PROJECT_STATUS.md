# Project status — v0.10.0 SOURCE SEALED (device acceptance pending)

- Repository: `aitishnyk/vacuum-voice-hub`
- Release candidate: **0.10.0** (154-model + 18-language script expansion)
- Parent sealed release: **v0.9.1** at `80aded56f094152873fdc8a5ce30f06fd41df79a`
- Model catalog: **154 profiles** = 109 preserved original IDs + 45 source-backed new identities.
- Voice catalog: **55 source-attributed voice variants**, unchanged. No third-party audio was mirrored by the expansion.
- Software matrix: **8,470 model × catalog-voice combinations**, not a physical install claim.
- Script templates: **18 text locales × 16 semantic phrases**, not additional prerecorded voice packs.
- New opt-in TTS capability: local `espeak-ng` generates WAV files to a Creator workspace; never silently downloads, synthesizes, builds or installs.
- Source version 0.10.0. Source release: **SEALED** after GitHub exact-head CI, public site, CodeQL, release-bundle and three-OS desktop package checks.
- v0.10.0 functional merge commit: `c58030234f0c4ea77077e4ed8c4a0059f9d9634a` (PR #16).

## Device truth and guardrails

- **Xiaomi X10 (`dreame.vacuum.r2209`) is still the only hardware-verified VVH device.**
- Every newly added model is `device_tested=false`, `unsupported-local`, `allow_default=false`, even if `--allow-experimental-transport` is supplied.
- New Dreame numeric profiles are conservative *family-format research conversions*, not verified package acceptance for their specific device/firmware.
- Newer models with unknown vendor layouts use non-installable `semantic_bundle`.
- Existing experimental transports and vendor-signed-only restrictions are unchanged.
- Source-only community recordings are not bundled, and no new audio-license claims are made.
- Desktop binaries are not claimed signed/notarized unless trusted release-signing evidence exists.

## New developer and user-facing functionality

- Search/filter CLI model list (`vvh models --search`, `--vendor`, `--adapter`, `--hardware-verified`).
- `vvh languages`: attributed catalog language codes separately from translated text templates.
- `vvh scripts list/show/export`: local read-only model-aware translation scripting.
- `vvh scripts synth ... --allow-synthetic`: optional local machine-generated WAVs and creator workspaces.
- Creator Studio multilingual text preview and clipboard export; local read-only JSON API.
- Public catalog separates audio-language statistics from text-only language templates.
- `vvh.script-pack.v1` schema and dedicated regression tests.
- Preservation baseline: `tests/fixtures/v08_model_identity.json` pins old IDs and aliases; exact catalog mirror and model-matrix audit check.

## Release/verification state

**SOURCE SEALED** on functional main commit `c58030234f0c4ea77077e4ed8c4a0059f9d9634a`.

- PR #16 head `fed6581ffb8905924a21210fc900b7334fda11c2`:
  - CI run `37853660290`: SUCCESS; **120 tests passed, 2 inherited python-miio deprecation warnings**;
  - Model Matrix audit: **154 models × 55 voice variants = 8470 software target combinations**;
  - PR checks run `37853657541`: SUCCESS;
  - Public Site run `37853660469`: SUCCESS;
  - Release Bundle run `37853660226`: SUCCESS;
  - Desktop Packages run `37853660227`: **SUCCESS (macOS, Windows, Linux)**, artifacts retained by GitHub Actions.
- On merged main commit:
  - CI run `37853891373`: SUCCESS;
  - Public Site run `37853891379`: SUCCESS;
  - CodeQL Python + GitHub Actions run `37853890859`: SUCCESS;
  - Dependency graph run `37853897990`: SUCCESS.

No signed/notarized desktop binaries are claimed. The GitHub Release/tag publication, real robot installs beyond the existing X10 evidence, and native-speaker review of all translated scripts remain separate release-acceptance gates.

## Incomplete external work

Hardware-specific package-format and installed-voice acceptance for Xiaomi H40/X20+, ROIDMI EVA/EVE, Viomi, Mijia 5/6 and newer Dreame remain unverified. See [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14). Localized prompts should be reviewed by native speakers before medical/safety warnings are used. CodeQL and build success are not equivalent to real-device approval.

Next proposed software wave: **v0.11.0 Voice Localization & Model Evidence** — [Issue #17](https://github.com/aitishnyk/vacuum-voice-hub/issues/17). Never advertise universal custom voice installation.
