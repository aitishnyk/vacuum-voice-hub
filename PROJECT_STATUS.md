# Project status — v0.11.0 SOFTWARE RELEASE CANDIDATE

- Canonical starting point: v0.10.0 sealed source `906d5551d0a3fd6c9dc4730fa69ec093b09a8d1d`.
- Model profiles **154**, attributed voice variants **55**, script text locales **18**, software matrix **8,470**.
- No new device ID or transport is promoted by v0.11. This wave improves actual local language/audio creation and review.
- New source scope: optional local Piper ONNX synth into Creator Studio; WAV amplitude/clipping/duration/silence QA; Creator workspace report, read-only API, CLI and UI button.
- Version `0.11.0`. **Source release candidate only** until exact-head GitHub CI, release bundle, public catalog, desktop and CodeQL results are checked.
- Xiaomi X10 (`dreame.vacuum.r2209`) is still the sole VVH physically verified target; all existing signed-only/build-only restrictions remain unchanged.
- Voice models are user-provided, local and separately licensed. Piper generated WAV assets are not asserted distributable, publicly available or tested on real robot hardware.
- Legacy 109 model IDs and aliases preserved by `tests/fixtures/v08_model_identity.json` and full v0.10 model/voice matrix audit.

## Remaining limitations

- No universal vendor custom-voice transport or signed-pack bypass claimed.
- Piper requires the locally installed executable, exact model ONNX+config and explicit `--allow-synthetic`.
- WAV QA is signal-only. Other source formats need conversion before measuring; pronunciation, language correctness and human listening still require review.
- Live device install/failure/rollback acceptance for H40/X20+, ROIDMI, Viomi and additional modern firmware remains pending in [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).
- Native-speaker translation expansion and additional source-verified models remain future scope.

See [docs/VOICE_QA_PIPER_V011.md](docs/VOICE_QA_PIPER_V011.md).
