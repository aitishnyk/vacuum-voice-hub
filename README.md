# Vacuum Voice Hub

[![CI](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)

**Credits-first multi-model voice-pack library, compatibility engine, converter and installer for robot vacuums.**

## v0.3 at a glance

- **55 attributed voice variants**
- **7 robot model profiles**
- **560+ observed semantic/numeric events**
- per-model coverage and core-event coverage
- category-specific fallback voices
- explicit transport evidence levels
- Xiaomi X10 remains the only VVH hardware-verified model
- local Web UI + CLI
- stock-voice restore where the model transport supports it

Supported model profiles:

- Xiaomi Robot Vacuum X10 — `dreame.vacuum.r2209` — hardware verified
- Dreame D9 — `dreame.vacuum.p2009` — build/coverage only
- Dreame D10S Plus — `dreame.vacuum.r2240` — MIoT-spec transport
- Dreame L10S Ultra — `dreame.vacuum.r2228o` — MIoT-spec transport
- Dreame L40 Ultra — `dreame.vacuum.r2492*` — community device research
- Dreame X40 Ultra — `dreame.vacuum.r2416*/r2449*` — experimental transport
- MOVA P10 Pro Ultra — `mova/dreame.vacuum.r2491*` — provisional profile / experimental transport

See [Model compatibility matrix](docs/MODEL_MATRIX.md).

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
vvh doctor
vvh stats
vvh web
```

## Compatibility before installation

```bash
vvh models
vvh model-info dreame.vacuum.r2228o
vvh coverage warcraft --model dreame.vacuum.r2228o
```

### Semantic fallback

```bash
vvh build warcraft \
  --model dreame.vacuum.r2228o \
  --fallback-category error=q0-russian \
  --fallback-category dock=q0-russian \
  --fallback uk-female-pensive
```

Category fallback is applied before the general fallback. Only event IDs known to the target model are packaged.

## Installation safety

VVH refuses to infer hardware support from a similar model.

- verified/spec/community transports may install according to the model policy;
- experimental transports require `--allow-experimental-transport`;
- unsupported transports fail closed;
- the robot model returned by miIO must match a declared alias;
- token is never printed;
- the HTTP server tracks whether the robot itself actually fetched the package.

Example:

```bash
vvh install maxim-full --model dreame.vacuum.r2209 --ip 192.168.1.123
```

For an experimental model:

```bash
vvh install glados-findus \
  --model dreame.vacuum.r2416a \
  --ip 192.168.1.123 \
  --allow-experimental-transport
```

Use that flag only when you understand that VVH has not physically verified the model.

## Credits and third-party audio

Every catalog entry stores upstream source, acknowledgement, source byte size, integrity data when available, adult marker and redistribution policy.

- [Catalog](catalog/CATALOG.md)
- [Credits](CREDITS.md)
- [Third-party audio policy](THIRD_PARTY_AUDIO.md)

Character audio is not mirrored merely because it is publicly downloadable. Source-only packs are fetched from the upstream project.

## Semantic event system

VVH maps common robot events to stable names such as `clean.start`, `error.main_brush`, `dock.return.charge` and `mapping.complete`.

See [SEMANTIC_EVENTS.md](docs/SEMANTIC_EVENTS.md).

## Physical verification

Only Xiaomi X10 currently has a VVH physical-install log proving Set Voice acceptance, HTTP download and success/100%.

See [TESTED_HARDWARE.md](docs/TESTED_HARDWARE.md).

## Support

Use the **Sponsor** button on GitHub to support source recovery, hardware testing and new model adapters.

## Next

v0.4 adds **Creator Studio** and the `vvh.voicepack.v1` semantic pack format. v0.5 follows with desktop packaging and privacy-safe community compatibility reports.

VVH is independent community software and is not affiliated with Xiaomi, Dreame, Roborock, MOVA, Trouver or third-party character rights holders.
