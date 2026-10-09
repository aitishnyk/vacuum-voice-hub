# v0.11 Offline Piper Voice Studio & Audio QA

## Two distinct ways to author languages

- `vvh scripts synth` uses a locally installed **eSpeak-NG** voice; the project already supports all 18 text-script locales with explicit TTS engine selection.
- `vvh scripts piper` uses a **user-provided, licensed** neural Piper ONNX model and its matching `.onnx.json` file. It does not fetch from Hugging Face, open remote URLs, enumerate cloud voices or update an existing workspace.

Official Piper-style usage: local `piper --model /path/voice.onnx --config /path/voice.onnx.json --output_file clip.wav`, with UTF-8 text supplied on stdin. See [Piper upstream](https://github.com/OHF-Voice/piper1-gpl) and [Piper voice samples](https://rhasspy.github.io/piper-samples/). Different voices can have independent licenses; inspect the voice's model card before redistribution.

## Commands

```bash
# Text script (not audio) for a target device
vvh scripts show --language uk --model dreame.vacuum.r2209

# Local neural voice; the ONNX and ONNX.JSON must already exist
vvh scripts piper \
  --language uk --model dreame.vacuum.r2209 \
  --id personal-uk-piper --author "Personal creator" \
  --voice-model /path/to/uk_UA-voice.onnx \
  --allow-synthetic

# A model with multiple supported speakers may accept a specific ID
vvh scripts piper --language ru --id sample-piper --author Me \
  --voice-model /path/to/ru_RU-voice.onnx --speaker 0 --allow-synthetic

# Read-only WAV QA; also available as Audio QA button in Creator Studio
vvh creator qa /path/to/project --model dreame.vacuum.r2209
```

Nothing is installed on a robot. The exact `model_id` and event IDs are derived from the catalog; proprietary voice-package acceptance is *not* inferred from the TTS result. Newer vendor-signed and unsupported models stay restricted.

## Safety and licensing guarantees

1. Piper CLI is searched only locally (`PATH`); the ONNX model must be an **existing path**, <=500 MiB, with adjacent JSON config <=256 KiB.
2. The config declares a language prefix matching the script locale; a mismatch fails before workspace creation.
3. Audio is synthesized by launching the executable with a structured argument array, not via a shell; each event is run with a 40-second limit.
4. Output is a new, separate Creator Studio workspace. Any failure cleans up only the just-created workspace.
5. All Piper-generated clips must be valid 16-bit PCM WAV (mono/stereo 8–96 kHz), <=25 MiB per clip. An SHA-256 fingerprint of the user-provided ONNX is included in the result for traceability. No raw voice model or audio is uploaded.
6. License state is `UNLICENSED` and `redistribution_verified=false` until the owner validates rights, speaker identity and quality. No automatic profanity/medical/safety validation of translated content is promised.
7. Successful synthesis and software compatibility **never authorize custom voice installation**. Device tests and transport evidence are tracked in [hardware Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

## Signal QA contract

`vvh.wav-audio-qa.v1` checks sample rate, channels, WAV format, duration, peak, RMS loudness, clipping fraction and approximate silence fraction. It flags <0.25-second / >180-second clips, very quiet RMS, >0.1% clipped samples and >95% silent samples. Results are **heuristics**, not subjective voice naturalness, pronunciation, engine licensing, copyright ownership or device acceptance. Only WAV can receive direct signal QA; other Creator audio formats are identified as `not-analyzed`, not silently accepted as clean. The `vvh.workspace-audio-qa.v1` report includes model-aware semantic/event coverage when a model is selected.

## Release checks

```bash
python -m pytest -q
python scripts/model_matrix_audit.py
python -m compileall -q vacuum_voice_hub
vvh scripts piper --help
vvh creator qa --help
vvh release build --output release
vvh release verify release
```

Source code is not considered production-ready for new robot transports without physical-device acceptance and verified rollback.
