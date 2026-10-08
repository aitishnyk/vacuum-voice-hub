# Vacuum Voice Hub

[![CI](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)

**Credits-first multi-model voice-pack platform for robot vacuums.**

## v0.6 platform

- **55 attributed voice variants**
- **7 robot model profiles**
- **560+ observed event IDs**
- `vvh.semantic.v1` compatibility layer
- `vvh.voicepack.v1` Creator Studio format
- `vvh.compat-report.v1` privacy-safe device evidence
- `vvh.public-catalog.v1` static public catalog
- desktop shell and macOS/Windows/Linux build matrix
- OS Keychain/Secret Service support
- local install history without token/IP/MAC
- fail-closed hardware evidence policy

## Run locally

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

## Public website/catalog

```bash
vvh site build --output public
vvh site verify public
```

The static output contains searchable voices, source credits, model compatibility plus machine-readable JSON and SHA-256 manifest.

Read [PUBLIC_CATALOG.md](docs/PUBLIC_CATALOG.md).

## Model profiles

- Xiaomi X10 `dreame.vacuum.r2209` — **VVH hardware verified**
- Dreame D9 `p2009` — build/coverage only
- Dreame D10S Plus `r2240` — MIoT-spec transport
- Dreame L10S Ultra `r2228o` — MIoT-spec transport
- Dreame L40 Ultra `r2492*` — community device research
- Dreame X40 Ultra `r2416*/r2449*` — experimental transport
- MOVA P10 Pro Ultra `r2491*` — provisional / experimental

See [MODEL_MATRIX.md](docs/MODEL_MATRIX.md).

## Creator Studio

```bash
vvh creator new --id my-pack --name "My Pack" --author "Me" --language en --license CC-BY-4.0
vvh creator events --model dreame.vacuum.r2209 --category cleaning
vvh creator build ~/path/to/my-pack --model dreame.vacuum.r2209
```

Read [CREATOR_STUDIO.md](docs/CREATOR_STUDIO.md).

## Credentials and install

```bash
pip install -e ".[security]"
vvh credential save home-x10
vvh install maxim-full --model dreame.vacuum.r2209 --ip 192.168.1.123 --credential home-x10
```

Unsupported transports fail closed; experimental transports require explicit opt-in.

## Community verification

```bash
vvh history --limit 20
vvh report --ip 192.168.1.123 --model dreame.vacuum.r2209 --credential home-x10
```

Reports intentionally exclude token, IP and MAC and are never uploaded automatically.

Read [COMMUNITY_VERIFICATION.md](docs/COMMUNITY_VERIFICATION.md).

## Credits

Every catalog entry retains source/credit metadata. Third-party character audio is source-linked rather than mirrored unless redistribution rights are clear.

- [Catalog](catalog/CATALOG.md)
- [Credits](CREDITS.md)
- [Third-party audio policy](THIRD_PARTY_AUDIO.md)

## Support

Use the **Sponsor** button on GitHub to support source recovery, hardware testing and model adapters.

## Evidence boundary

Software/profile support is not the same as physical-device verification. Only reviewed real-device evidence may promote a model to hardware verified.

VVH is independent community software and is not affiliated with robot-vacuum vendors or third-party character rights holders.
