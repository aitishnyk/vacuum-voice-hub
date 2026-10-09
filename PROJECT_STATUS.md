# Project status — v0.12.0 SOFTWARE RELEASE CANDIDATE

- Starting source: v0.11.0 merged `c02a0d918e27eceb33b62b2cb6cef2b520da4ed7`.
- Source version: **0.12.0**; **NOT SEALED** until exact GitHub CI, Public Site, Release Bundle and desktop gates pass.
- Models: **154**; source-attributed real audio variants: **55**; built-in text locales: **18**; target combinations: **8,470**.
- Historical 109 model identity/alias baseline, all 154 v0.10 profiles and all 55 catalog voices preserved.
- New: model-aware translation reference scaffolding; strict local `vvh.translation-overlay.v1`; per-model translation coverage audit and optional extension for local eSpeak-NG/Piper TTS.
- 16 original template phrases per locale remain intact with no overlays; extra translated event prompts come from user-supplied, attribution-labelled local JSON.
- Version `vvh.script-pack.v1` and existing local/Creator voice workflows remain compatible.
- Native-speaker review and actual audio license grants are **NOT implied** by author/declared license strings.
- No change to `device_tested`: X10 (`dreame.vacuum.r2209`) remains the **only physically verified VVH target**.
- Signed-only/new modern custom install remains blocked; source-backed family profiles do not imply installed-voice acceptance.

## Acceptance gates

Check v0.12 exact PR head and merged main workflows before marking source sealed. Actual external hardware, signed/notarized desktop distributions and trusted locale correctness remain separate gates.

## Next priorities

- v0.13: source-backed additional device identities, genuine licensed voice packs and review workflow without breaking the model/voice catalogs.
- v1.0 requires genuine device/firmware confirmation per [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

See [v0.12 Translation Overlays](docs/TRANSLATION_OVERLAYS_V012.md).
