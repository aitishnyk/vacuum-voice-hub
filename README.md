# Vacuum Voice Hub

[![CI](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml)

**Credits-first multi-model voice platform for robot vacuums.**

## v0.10.0 — Expanded Model & Language Studio

The v0.9.1 security update replaces legacy archive extraction with bounded, symlink-safe ZIP/TAR streaming on Python 3.10+; unsafe archive names, special members, collisions and excessive sizes fail closed.


Vacuum Voice Hub v0.10 provides **154 model profiles** and retains **55 source-attributed recorded voice variants** — an **8,470 software model × voice target** matrix. It additionally provides **18 text-only script locales** (16 common event prompts each) and optional local espeak-ng WAV synthesis into Creator Studio.

Target families:

- **51 Dreame numeric** targets;
- **33 Roborock** targets;
- **8 IJAI** targets;
- **62 portable semantic/build-only** targets.

All targets participate in model-aware compatibility, preview and Creator Studio. Installation remains evidence-scoped: Xiaomi X10 is the only VVH hardware-verified device; experimental or vendor-signed limitations are shown explicitly.

Read [v0.10 Expansion & Language Studio](docs/MODEL_LANGUAGE_EXPANSION_V010.md), [Mass Model Expansion](docs/MASS_MODEL_EXPANSION.md), the full [Model Matrix](docs/MODEL_MATRIX.md), and the [v0.9 Offline Research Workflow](docs/RESEARCH_WORKFLOW_V09.md).

### New in v0.9 — offline package research

- safe bounded archive inventory for ZIP/TAR without extracting or running untrusted files;
- SHA-256 + size validation of exact candidate against optional vvh.transport-evidence.v1 reports;
- conservative numeric OGG, IJAI MP3 and Roborock WAV filename-pattern discovery;
- cross-check against the chosen model's declared event profile;
- versioned research schemas, CLI and negative regression tests;
- opaque proprietary .pkg metadata intake without decryption or installation.

```bash
vvh research inspect ./candidate.zip --model xiaomi.vacuum.d101
vvh research validate-evidence ./evidence.json --model xiaomi.vacuum.d101
vvh research inspect ./candidate.zip --model xiaomi.vacuum.d101 --evidence ./evidence.json
```

**v0.9 does not certify new custom-install transports.** Filename similarities and community reports do not constitute robot hardware tests. Build-only/official-signed-only restrictions remain in force.

## New commands in v0.10

```bash
vvh models --search "Dreame"
vvh models --adapter semantic_bundle
vvh models --hardware-verified
vvh languages
vvh scripts list
vvh scripts show --language ru --model xiaomi.vacuum.d101
vvh scripts export --language uk --model dreame.vacuum.r2209 --output ./uk-script.json
```

**Optional local synthetic audio** (no cloud TTS; requires `espeak-ng` installed):

```bash
vvh scripts synth --language ru --model dreame.vacuum.r2209 \
  --id custom-russian --author "Local author" --voice ru --allow-synthetic
```

This produces a private Creator workspace with generated WAV files; it does **not** automatically install audio on any robot. Text-only scripts are not counted as available prerecorded voice packs, and the quality/redistribution rights of local TTS must be reviewed.

## Main capabilities

- 55 source-attributed community voice variants;
- Russian, Ukrainian, English and additional language packs;
- 18+ packs hidden by default;
- semantic event namespace and category fallback;
- target-specific event filtering;
- Dreame numeric OGG `tar.gz` builds;
- classic Roborock named-WAV / `.pkg` builds;
- IJAI named-MP3 ZIP builds;
- portable non-installable semantic bundles for unknown families;
- Creator Studio `vvh.voicepack.v1`;
- desktop UI for macOS / Windows / Linux;
- privacy-safe install history and `vvh.compat-report.v1`;
- searchable public catalog;
- reproducible release bundles, SPDX SBOM and SHA256 verification;
- offline package forensics and privacy-safe evidence assessment (v0.9).

## Local app

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
vvh doctor
vvh web
```

Desktop:

```bash
pip install -e ".[desktop]"
vvh-desktop
```

## Find a model

```bash
vvh models
vvh model-info xiaomi.vacuum.d101
vvh model-info roborock.vacuum.s5
vvh model-info ijai.vacuum.v2
```

The Web UI and Creator Studio include model search.

## Check a voice without installing

```bash
vvh coverage warcraft --model xiaomi.vacuum.d101
vvh coverage maxim-full --model roborock.vacuum.s5
```

Coverage uses the canonical semantic layer and does not need to build an encrypted/vendor package.

## Build a target package

```bash
vvh build maxim-full --model dreame.vacuum.r2228o
vvh build maxim-full --model ijai.vacuum.v2
vvh build maxim-full --model xiaomi.vacuum.d101
```

Classic Roborock encrypted `.pkg` output additionally requires `ccrypt`.

## Install policy

VVH fails closed.

- X10: hardware verified.
- Known but unverified local transports: explicit `--allow-experimental-transport`.
- Newer vendor-signed Roborock: arbitrary custom install blocked.
- Unknown Xiaomi/Viomi/ROIDMI/etc transports: build/preview/coverage only.

Example experimental installation:

```bash
vvh install maxim-full \
  --model roborock.vacuum.s5 \
  --ip 192.168.1.123 \
  --credential home-robot \
  --allow-experimental-transport
```

Never treat model similarity as physical verification.

## Creator Studio

```bash
vvh web
```

Open `/creator` and build one semantic voice project for many target families.

## Community verification

```bash
vvh report --ip 192.168.1.123 --model dreame.vacuum.r2209 --credential home-x10
```

Reports omit token, IP and MAC and are never uploaded automatically.

## Public catalog and reproducible releases

```bash
vvh site build --output public
vvh site verify public

vvh release build --output release
vvh release verify release
```

See [DISTRIBUTION.md](docs/DISTRIBUTION.md).

## Credits

Every community voice entry retains its upstream source and credit metadata.

- [Credits](CREDITS.md)
- [Catalog](catalog/CATALOG.md)
- [Third-party audio policy](THIRD_PARTY_AUDIO.md)

VVH is independent community software and is not affiliated with Xiaomi, Mijia, Dreame, Roborock, IJAI, Viomi, ROIDMI, Smartmi or third-party character rights holders.
