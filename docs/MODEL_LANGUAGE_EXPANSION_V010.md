# v0.10.0 — Expanded Robot Profiles & Multilingual Voice Studio

## What is added

The catalog merges **45 new source-attributed Dreame/Xiaomi/MOVA model IDs** while preserving the exact previous **109 model IDs and aliases**. The resulting **154 catalog profiles** are compatible with the existing semantic build/preview pipeline for 55 attributed voice variants. This is **8,470 software model × voice target combinations**, **not 8,470 physically confirmed custom voice installations**.

Canonical inventory sources:
- Dreame Vacuum supported-device reference: https://dv.tasshack.com/ru/guide/more/supported-devices
- Historical Dreame model references: https://github.com/matjahs/dreame-vacuum
- Valetudo supported robots (separate firmware platform; do not conflate with vendor custom voice install): https://valetudo.cloud/pages/general/supported-robots/

The 45 imported IDs omit fictional Mi Home `product_id` and `plugin_id` numbers. Historical models retain those values verbatim. Two L40 Ultra regional IDs already existed as aliases (`r2492b`, `r2492j`) and were **not** inserted a second time. No legacy model ID or alias is lost.

**Every newly imported device is build/preview/research-only**. The earlier Dreame-family research candidate group uses a conservative `dreame_numeric` OGG/tar.gz conversion profile without claim of exact-device voice layout; modern variants use a portable non-installable semantic bundle. None receives a new verified transport or device_tested=true.

## 18 translated script locales

The `vvh.script-pack.v1` data contract contains **16 common system/cleaning/error/dock events** translated into:

- English (en), Russian (ru), Ukrainian (uk), German (de), French (fr), Spanish (es);
- Italian (it), Portuguese (pt), Dutch (nl), Polish (pl), Czech (cs), Slovak (sk);
- Hungarian (hu), Romanian (ro), Turkish (tr), Japanese (ja), Korean (ko), Simplified Chinese (zh-Hans).

**These are text prompts, not prerecorded community voice variants.** The 55 attributed source-linked voice variants and original seven recorded language codes remain unchanged. TTS pronunciations/translations may need native-speaker review, especially warnings and safety prompts.

Use the templates for recording, licensed professional TTS, or optional **local** espeak-ng speech synthesis. The system never downloads audio or asks a cloud service to speak on your behalf.

## Commands

```bash
vvh models --search "L40"
vvh models --adapter semantic_bundle
vvh models --hardware-verified
vvh languages
vvh scripts list
vvh scripts show --language ru --model xiaomi.vacuum.d101
vvh scripts export --language uk --model dreame.vacuum.r2228o --output ./uk-script.json
```

`scripts export` refuses to overwrite existing files. Every exported phrase includes its canonical semantic key and exact target-model event IDs or an empty array when the device profile does not include that semantic event.

### Generate **real** local synthetic WAVs (optional)

Install `espeak-ng` separately. Choose an **installed voice ID** explicitly; language templates alone do not guarantee a matching TTS voice exists on your system.

```bash
vvh scripts synth \
  --language ru \
  --model dreame.vacuum.r2209 \
  --id my-local-ru-robot \
  --author "Local creator" \
  --voice ru \
  --speed 160 \
  --pitch 50 \
  --allow-synthetic
```

This generates 16 local WAV files in a newly created Creator Studio workspace using `espeak-ng`. It refuses existing output directories, does not use the network and does not automatically build or install onto a robot. Generated audio is marked `UNLICENSED` until the author verifies the engine voice and intended redistribution rights. After listening/reviewing and fixing the audio, build explicitly:

```bash
vvh creator validate ~/.local/share/vacuum-voice-hub/creator/my-local-ru-robot
vvh creator build ~/.local/share/vacuum-voice-hub/creator/my-local-ru-robot --model dreame.vacuum.r2209
```

Creator Studio UI (`vvh web`, then `/creator`) now supports model-aware script preview, locale selection and copying to clipboard. The Web API offers local read-only `/api/script-locales` and `/api/script?language=ru&model_id=...` routes. Public catalog reports recorded languages **separately** from script-only locales.

## Installation safety

The existing X10 physical transport evidence remains the **only** VVH hardware verification. All new models are non-installable by default and resist `--allow-experimental-transport`. Vendor-signed models remain signed-only. Neither Valetudo support, an upstream integration's model ID, a working script, a generated WAV, nor a family-format package alone proves custom voice installation on a given device.

## QA and preservation

The `tests/fixtures/v08_model_identity.json` baseline freezes all 109 historical model IDs and aliases. The model matrix audit checks those identities still resolve to the same canonical devices, all 154 profiles retain runtime adapters/event profiles and only one model is device_tested. The 55 original voice records are untouched. All 18 script locales must provide exactly the same 16 semantic events, and synthesis requires explicit consent.

Hardware acceptance for further families is tracked separately in [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).
