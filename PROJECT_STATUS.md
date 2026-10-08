# Project status — v0.10.0 SOFTWARE RELEASE CANDIDATE

- Repository: `aitishnyk/vacuum-voice-hub`
- Release candidate: **0.10.0** (154-model + 18-language script expansion)
- Parent sealed release: **v0.9.1** at `80aded56f094152873fdc8a5ce30f06fd41df79a`
- Model catalog: **154 profiles** = 109 preserved original IDs + 45 source-backed new identities.
- Voice catalog: **55 source-attributed voice variants**, unchanged. No third-party audio was mirrored by the expansion.
- Software matrix: **8,470 model × catalog-voice combinations**, not a physical install claim.
- Script templates: **18 text locales × 16 semantic phrases**, not additional prerecorded voice packs.
- New opt-in TTS capability: local `espeak-ng` generates WAV files to a Creator workspace; never silently downloads, synthesizes, builds or installs.
- Source version 0.10.0. SOURCE RELEASE: **CANDIDATE until exact-head CI, release, public site and desktop gates pass.**

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

Once CI completes, update this section with exact successful workflow/run evidence. Do **not** mark source sealed or production ready merely because a pull request exists.

## Incomplete external work

Hardware-specific package-format and installed-voice acceptance for Xiaomi H40/X20+, ROIDMI EVA/EVE, Viomi, Mijia 5/6 and newer Dreame remain unverified. See [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14). Localized prompts should be reviewed by native speakers before medical/safety warnings are used. CodeQL and build success are not equivalent to real-device approval.

Next proposed software wave: **v0.11.0 Voice Localization & Model Evidence**. Never advertise universal custom voice installation.
