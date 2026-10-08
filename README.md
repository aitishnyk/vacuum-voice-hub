# Vacuum Voice Hub

[![CI](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)

**Open voice-pack library, compatibility engine, converter and installer for robot vacuums.**

Vacuum Voice Hub (VVH) turns community voice packs into model-specific packages while preserving the original creator/source attribution.

> Hardware-verified target: **Xiaomi Robot Vacuum X10 / `dreame.vacuum.r2209`**.
> The architecture is multi-model by design: future Dreame, Xiaomi, Roborock, Mova and Trouver support lives in independent model adapters.

## v0.2 — 50 Voice Wave + Compatibility Engine

v0.2 grows VVH from a working X10 installer into a compatibility-aware catalog:

- **55 attributed voice variants** across **7 languages**;
- **13 explicit/18+ variants**, hidden by default in the Web UI;
- conservative **106-event X10 hardware-verified profile**;
- semantic event metadata and model event profiles;
- model-specific **coverage score** and core-event coverage;
- optional **fallback voice** to fill missing X10 events;
- safe filtering of extra/unverified event IDs from X10 builds;
- remote legacy Roborock **`.pkg`** sources through the historical ccrypt format;
- **31 research/recovery records**, including 18 old packs with preserved historical URL + MD5 + size metadata;
- clearer source verification labels: Git blob, MD5, byte size, or release metadata;
- compatibility-aware local Web UI.

“Convertible” means VVH understands the source format. It does **not** mean that every community pack has been physically exercised on every robot.

## Why this project exists

Robot-vacuum voice packs are scattered across GitHub, 4PDA, old Xiaomi/Roborock communities and personal archives. File layouts, event IDs and codecs differ by generation and model. VVH provides one credits-first catalog and a conversion pipeline without pretending that all numeric sound IDs are universal.

## Install on macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
vvh doctor
vvh stats
vvh web
```

Or use `scripts/INSTALL_MACOS.command`.

## CLI examples

```bash
# Browse
vvh stats
vvh list --language ru
vvh list --adult
vvh info maxim-full

# Measure compatibility before installing
vvh coverage l40-jarvis --model dreame.vacuum.r2209

# Fill missing model events from another pack
vvh coverage l40-jarvis --model dreame.vacuum.r2209 --fallback q0-russian
vvh build l40-jarvis --model dreame.vacuum.r2209 --fallback q0-russian

# Install
vvh install maxim-full --model dreame.vacuum.r2209 --ip 192.168.1.123

# Legacy Roborock .pkg from the catalog
# Requires: brew install ccrypt
vvh coverage phil-british-butler --model dreame.vacuum.r2209
```

The local token is requested interactively when omitted and is never printed.

## Compatibility model

VVH v0.2 does **not** assume that “Dreame numeric OGG” means universal compatibility.

For X10, the profile `x10-known-v1` contains **106 event IDs** derived from the event layout used by the package that was accepted by a physical X10. A source pack is measured against that profile:

```text
source archive
  ↓ source-format adapter
canonical numeric events
  ↓ Compatibility Engine
covered / missing / extra / core coverage
  ↓ optional fallback fill
X10 verified-safe event subset
  ↓ package + install
```

Newer L40/X40-family packs can contain hundreds of additional IDs. VVH reports those as `extra` and does not put them into an X10 package until they are verified for that model.

## Fallback

A partial character pack can be combined at build time with a second pack:

```bash
vvh build <character-pack> --fallback <base-pack>
```

Only missing IDs that are part of the target model's known event profile are copied. The original source archives are never modified.

## Source integrity and credits

Every catalog entry includes:

- upstream project/source page;
- acknowledgement text;
- language and explicit-content marker;
- original model/layout where known;
- source byte size;
- Git blob SHA and/or MD5 where available;
- redistribution policy;
- source verification level.

See [catalog/CATALOG.md](catalog/CATALOG.md) and [CREDITS.md](CREDITS.md).

**VVH does not mirror third-party character audio by default.** It downloads from the original/upstream location at build time. See [THIRD_PARTY_AUDIO.md](THIRD_PARTY_AUDIO.md).

## Import your own pack

```bash
# Dreame/Valetudo tar.gz, RoboVoice MP3 archive, Ijai ZIP,
# old Roborock named audio, or historical Roborock .pkg
vvh import-pack ~/Downloads/my_voice.pkg --model dreame.vacuum.r2209
```

Legacy Roborock `.pkg` decoding requires `ccrypt` (`brew install ccrypt`). The historical community package key is used only for that old file format.

## Official voices / restore

```bash
vvh stock --model dreame.vacuum.r2209
vvh restore-stock RU --model dreame.vacuum.r2209 --ip 192.168.1.123
```

VVH discovers official Dreame packages from the manufacturer's `soundpackage.json` at runtime rather than mirroring them.

## Physical X10 evidence

On a real `dreame.vacuum.r2209`, firmware `4.3.9_1321`:

- Set Voice at `siid=7 / piid=4` returned `code=0`;
- the robot fetched the generated package over the LAN;
- the custom voice packet ID was set;
- state changed `downloading → success`;
- progress reached `100`.

That verifies the **transport and package path**. Individual community voices still need their own hardware reports.

## Support the project

If VVH saves you time or helps bring custom voices to another robot model, you can support development through the **Sponsor** button on GitHub.

Sponsorship helps fund source recovery, compatibility research, hardware testing and new model adapters.

## Contributing

The most valuable contributions are:

- a real voice archive with its original source/author;
- a physical-device compatibility report;
- event mappings for another robot model;
- corrected attribution;
- original, redistributable voice packs.

See [CONTRIBUTING.md](CONTRIBUTING.md), [docs/ADDING_VOICE.md](docs/ADDING_VOICE.md) and [docs/ADDING_MODEL.md](docs/ADDING_MODEL.md).

VVH is independent community software and is not affiliated with Xiaomi, Dreame, Roborock, Mova, Trouver, Valve, Disney, Warner Bros., Blizzard or other rights holders.
