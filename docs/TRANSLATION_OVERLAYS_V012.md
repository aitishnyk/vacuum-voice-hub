# v0.12 Local Translation Overlays — Model-Aware Voice Packs

The original 18 language templates contain 16 recorded-script **texts**, not 18 finished voice packs. Version 0.12 enables contributors to translate additional *real catalog semantic events* without pretending that automated output is a complete or certified vendor voice pack.

## Step 1. Create an untranslated reference scaffold

```bash
vvh scripts scaffold --language uk --model dreame.vacuum.r2209 --output uk-reference.json
```

The generated file lists semantic event keys, English reference strings, and model-specific numeric IDs. **English references are not translated.** The scaffold's `translations` mapping is intentionally empty until a translator supplies target-language text.

## Step 2. Create a reviewed translation overlay

Store the following as `uk-overrides.json` (illustrative example; have a native speaker review it):

```json
{
  "schema": "vvh.translation-overlay.v1",
  "locale": "uk",
  "author": "Local translator",
  "license": "UNLICENSED",
  "source_url": null,
  "translations": {
    "error.bumper": "Перевірте бампер робота.",
    "clean.start": "Починаю прибирання."
  }
}
```

This example adds `error.bumper` beyond the original 16 phrases and overrides `clean.start` without modifying the base catalog.

The file is local and capped at 128 KiB, maximum 512 unique catalog semantic keys and 400 characters per translated phrase. Unknown event keys, duplicate JSON keys, blank translations, control characters, ambiguous locales or invalid source attribution fail closed. The overlay never modifies device IDs, event numeric IDs, transport commands, vendor package metadata or installation policy.

## Step 3. Audit target-model coverage

```bash
vvh scripts audit --language uk --model dreame.vacuum.r2209 --overlay ./uk-overrides.json
vvh scripts show --language uk --model dreame.vacuum.r2209 --overlay ./uk-overrides.json
vvh scripts export --language uk --model dreame.vacuum.r2209 \
  --overlay ./uk-overrides.json --output ./uk-script-for-robot.json
```

The report distinguishes:
- **scripted_count** — target-language phrases supplied (including any unmapped semantics);
- **mapped_count** — phrases which map to at least one ID supported by the target's conservative event profile;
- **model_event_count** — numeric IDs known for the target profile;
- **mapped_event_count / model_event_coverage_pct** — how many numeric IDs the supplied phrases reach;
- **overlay_count / overlay_attribution** — provenance of user translations, always `reviewed=false` at software intake.

A 100% text coverage metric would not prove audible pronunciation, all vendor statuses or physical installation support.

## Step 4. Optionally synthesize locally

```bash
vvh scripts synth --language uk --model dreame.vacuum.r2209 \
  --id espeak-uk-extra --author "Local creator" --voice uk \
  --overlay ./uk-overrides.json --allow-synthetic

vvh scripts piper --language uk --model dreame.vacuum.r2209 \
  --id piper-uk-extra --author "Local creator" \
  --voice-model /path/to/uk_UA-voice.onnx \
  --overlay ./uk-overrides.json --allow-synthetic

vvh creator qa /path/to/generated/workspace --model dreame.vacuum.r2209
```

Piper and eSpeak each require appropriate preinstalled local voices and separate redistribution-license review. Output is a **new Creator workspace**, never an auto-install. User-supplied translations may need pronunciation corrections and legal/safety review before use.

## Boundaries and preservation

- Original **154 model profiles and all aliases** remain; no new arbitrary custom-install permission.
- Existing **55 source-attributed voice variants** remain unchanged; user text or generated WAVs do not change these counts automatically.
- All **18 built-in text locales and 16 essential phrases** remain backward compatible without `--overlay`.
- Input provenance is recorded, not independently verified; declaring a license in JSON does not itself confer rights.
- For actual H40, ROIDMI, Viomi, Mijia and Roborock custom transport research see [hardware acceptance Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

## Validation

```bash
python -m pytest -q tests/test_translation_overlays_v012.py
python -m pytest -q
python scripts/model_matrix_audit.py
vvh release build --output ./release
vvh release verify ./release
```
