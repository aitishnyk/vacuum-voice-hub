# Project status — v0.12.0 SOURCE SEALED (hardware acceptance pending)

- Starting source: v0.11.0 merged `c02a0d918e27eceb33b62b2cb6cef2b520da4ed7`.
- Source version: **0.12.0**, **SOURCE SEALED** with exact-head CI, public catalog, release bundle, all three desktop packages and merged-main CodeQL confirmed.
- Functional release merged at `b3674acb18d15dc0c87f43a7365ae0aad32e8aee` (PR #20).
- Models: **154**; source-attributed real audio variants: **55**; built-in text locales: **18**; target combinations: **8,470**.
- Historical 109 model identity/alias baseline, all 154 v0.10 profiles and all 55 catalog voices preserved.
- New: model-aware translation reference scaffolding; strict local `vvh.translation-overlay.v1`; per-model translation coverage audit and optional extension for local eSpeak-NG/Piper TTS.
- 16 original template phrases per locale remain intact with no overlays; extra translated event prompts come from user-supplied, attribution-labelled local JSON.
- Version `vvh.script-pack.v1` and existing local/Creator voice workflows remain compatible.
- Native-speaker review and actual audio license grants are **NOT implied** by author/declared license strings.
- No change to `device_tested`: X10 (`dreame.vacuum.r2209`) remains the **only physically verified VVH target**.
- Signed-only/new modern custom install remains blocked; source-backed family profiles do not imply installed-voice acceptance.

## Verified exact-source gates

Pre-merge PR #20 head `3fcc2cea0a665cccd7617f162fca182cdafd53e4`:
- CI run `37900007033`: **SUCCESS**, 145/145 tests, 2 inherited python-miio deprecation warnings, Model Matrix **154 × 55 = 8,470** PASS;
- second CI run `37900011195`: SUCCESS;
- PR CodeQL `37900004207`: SUCCESS;
- Release Bundle `37900007214`: SUCCESS;
- Public Site `37900007199`: SUCCESS;
- Desktop Packages `37900007065`: SUCCESS for macOS / Linux / Windows.

On merged main `b3674acb18d15dc0c87f43a7365ae0aad32e8aee`:
- CI `37900220960`: SUCCESS;
- Public Site `37900220967`: SUCCESS;
- CodeQL Python + Actions `37900221131`: SUCCESS;
- dependency graph `37900228812`: SUCCESS.

This source sign-off does **not** imply binary notarization/signing, validation of local Piper/eSpeak voices on user machines, native-speaker sign-off or physical acceptance beyond the previously verified Xiaomi X10. No new vendor voice installation transports are claimed.

## Next priorities

- v0.13: source-backed additional device identities, genuine licensed voice packs and review workflow without breaking the model/voice catalogs.
- v1.0 requires genuine device/firmware confirmation per [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

See [v0.12 Translation Overlays](docs/TRANSLATION_OVERLAYS_V012.md).
