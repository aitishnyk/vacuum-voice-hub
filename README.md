# Vacuum Voice Hub

[![CI](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)

**Open voice-pack library, converter and installer for robot vacuums.**

Vacuum Voice Hub (VVH) turns community voice packs into model-specific packages and installs them without forcing every voice author to rebuild their work for every robot model.

> First production-tested target: **Xiaomi Robot Vacuum X10 / `dreame.vacuum.r2209`**.
> The architecture is intentionally multi-model: Dreame, Xiaomi, Roborock, Mova, Trouver and other adapters can be added independently.

## Why this project exists

Robot-vacuum voice packs are scattered across GitHub, 4PDA, old Xiaomi/Roborock communities and personal archives. File layouts, event IDs and codecs differ between models. VVH provides one catalog and one conversion pipeline while preserving attribution to the people who actually created the packs.

## What v0.1 includes

- catalog of installable community voice sources;
- author/source/credits metadata for every entry;
- 18+ labels and language/category filters;
- Git blob/MD5/size source verification;
- adapters for Dreame canonical `N.ogg` packs and RoboVoice/Trouver `NNN.mp3` packs;
- automatic audio normalization to Ogg Vorbis, 16 kHz, mono for X10;
- local-LAN installation through MIoT `siid 7 / piid 4`;
- honest installation status from `piid 3`;
- CLI and local web UI;
- model adapter registry designed for future vacuums;
- research backlog for discovered packs whose original archive still needs recovery.

## Install on macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
vvh doctor
vvh list
vvh web
```

Or use `scripts/INSTALL_MACOS.command`.

## CLI examples

```bash
vvh models
vvh list --language ru
vvh list --adult
vvh info maxim-full
vvh build maxim-full --model dreame.vacuum.r2209
vvh install maxim-full --model dreame.vacuum.r2209 --ip 192.168.0.106
```

The token is requested interactively when omitted and is never printed.

## Audio policy

**The repository does not mirror third-party character audio by default.** Many community packs contain game, film or cartoon material whose redistribution status is unclear. VVH stores source links, hashes, metadata and conversion recipes, then downloads from the original/upstream source at build time. See [THIRD_PARTY_AUDIO.md](THIRD_PARTY_AUDIO.md).

## Credits

This project is deliberately attribution-first. See [CREDITS.md](CREDITS.md). Every catalog record includes its upstream source and acknowledgement text.

## Safety

Installing a custom voice is an unsupported modification on many devices. VVH verifies the model before sending a package and refuses cross-model installation unless explicitly supported by the model adapter. It never needs your Xiaomi UID/DID for the local X10 path.

## Status

- `dreame.vacuum.r2209`: installation transport and package acceptance **tested on a physical device** with firmware `4.3.9_1321`.
- Individual upstream voice packs: marked separately as `tested`, `convertible`, `experimental`, or `research`.

VVH is community software and is not affiliated with Xiaomi, Dreame, Roborock, Mova, Trouver, Valve, Disney, Warner Bros., Blizzard or other rights holders.

## Import your own pack

```bash
# Dreame/Valetudo tar.gz, RoboVoice MP3 archive, Ijai ZIP, or old Roborock .pkg
vvh import-pack ~/Downloads/my_voice.pkg --model dreame.vacuum.r2209
```

Old Roborock `.pkg` import requires `ccrypt` (`brew install ccrypt` on macOS). The legacy community key is used only to decode that historical pack format.

## Official voices / restore

```bash
vvh stock --model dreame.vacuum.r2209
vvh restore-stock RU --model dreame.vacuum.r2209 --ip 192.168.0.106
```

VVH discovers stock Dreame packages from the manufacturer's `soundpackage.json` at runtime rather than mirroring them.
