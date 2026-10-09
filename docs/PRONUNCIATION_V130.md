# v1.3 — Opt-in local pronunciation glossary

A local pronunciation lexicon is supplied by a contributor. It changes
only the text passed to an **already installed** offline Piper/eSpeak
engine, never original translations or device events.

Example `glossary.json`:

```json
{
  "schema": "vvh.pronunciation-lexicon.v1",
  "locale": "uk",
  "author": "Local speaker",
  "license": "UNLICENSED",
  "entries": [
    {"written": "прибирання", "spoken": "прибирАння"}
  ]
}
```

```bash
vvh scripts pronounce --language uk --model dreame.vacuum.r2209 --lexicon ./glossary.json
vvh scripts piper --language uk --model dreame.vacuum.r2209 \
  --id local_uk --author "Creator" --voice-model ./licensed-local-voice.onnx \
  --allow-synthetic --lexicon ./glossary.json
# scripts synth accepts the same --lexicon option for local espeak-ng
```

Each substitution is literal and applied exactly once; user input is
escaped before regex matching and never reinterpreted as commands or
further substitutions. Lexicons are bounded to 64 KiB and 128 entries,
must declare locale, author and license, and are bound by SHA-256 in the
engine report. All synthesis remains opt-in and local.

The contributor's pronunciations, accent, native fluency and licensing
are **not automatically verified**. Review the synthesized audio before
redistribution. No new robot hardware, vendor transport or firmware
install is enabled by this feature.
