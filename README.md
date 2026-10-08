# Vacuum Voice Hub

[![CI](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)

**Credits-first multi-model voice-pack platform for robot vacuums.**

Vacuum Voice Hub combines a source-attributed voice catalog, semantic compatibility engine, model adapters, Creator Studio, desktop shell and privacy-safe community verification.

## v0.5

- **55 attributed community voice variants**
- **7 model profiles**
- **560+ observed event IDs**
- semantic namespace `vvh.semantic.v1`
- semantic authoring format `vvh.voicepack.v1`
- community report format `vvh.compat-report.v1`
- Creator Studio
- native desktop shell via pywebview
- macOS / Windows / Linux packaging workflow
- local install history with secret/network redaction
- optional OS Keychain / Secret Service token storage
- fail-closed transport evidence policy

## Start

CLI + browser UI:

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

Creator Studio is available at `/creator` in both browser and desktop modes.

## Model profiles

- Xiaomi X10 `dreame.vacuum.r2209` — **VVH hardware verified**
- Dreame D9 `p2009` — build/coverage only
- Dreame D10S Plus `r2240` — MIoT-spec transport
- Dreame L10S Ultra `r2228o` — MIoT-spec transport
- Dreame L40 Ultra `r2492*` — community device research
- Dreame X40 Ultra `r2416*/r2449*` — experimental transport
- MOVA P10 Pro Ultra `r2491*` — provisional profile / experimental transport

See [MODEL_MATRIX.md](docs/MODEL_MATRIX.md).

## Semantic fallback

```bash
vvh build warcraft \
  --model dreame.vacuum.r2228o \
  --fallback-category error=q0-russian \
  --fallback-category dock=q0-russian
```

Only event IDs known to the selected model profile are packaged.

## Creator Studio

```bash
vvh creator new --id my-pack --name "My Pack" --author "Me" --language en --license CC-BY-4.0
vvh creator events --model dreame.vacuum.r2209 --category cleaning
vvh creator validate ~/path/to/my-pack
vvh creator build ~/path/to/my-pack --model dreame.vacuum.r2209
```

Read [CREATOR_STUDIO.md](docs/CREATOR_STUDIO.md).

## Keychain / Secret Service

Install optional support:

```bash
pip install -e ".[security]"
vvh credential save home-x10
vvh credential status home-x10
```

Use it without exposing a token in the shell command:

```bash
vvh install maxim-full \
  --model dreame.vacuum.r2209 \
  --ip 192.168.1.123 \
  --credential home-x10
```

The status command never prints the token.

## Install history

```bash
vvh history --limit 20
```

History is local and intentionally strips token, IP, MAC and local URLs. Successful install history records download confirmation and final state, which can later support a community verification report.

## Community verification

```bash
vvh report \
  --ip 192.168.1.123 \
  --model dreame.vacuum.r2209 \
  --credential home-x10
```

The generated `vvh.compat-report.v1` file contains model/firmware/profile/transport/current voice state and sanitized latest-install evidence. It excludes token, IP and MAC, and is **not uploaded automatically**.

Read [COMMUNITY_VERIFICATION.md](docs/COMMUNITY_VERIFICATION.md).

## Desktop packages

`.github/workflows/desktop.yml` builds PyInstaller artifacts for macOS, Windows and Linux. Binary build success does not imply code signing/notarization.

Read [DESKTOP.md](docs/DESKTOP.md).

## Credits and third-party audio

Every catalog entry retains upstream source/credit metadata. Character audio is source-linked rather than mirrored unless redistribution rights are clear.

- [Catalog](catalog/CATALOG.md)
- [Credits](CREDITS.md)
- [Third-party audio policy](THIRD_PARTY_AUDIO.md)

## Safety / evidence policy

VVH does not mark hardware support from model similarity. Unsupported transports fail closed and experimental transports require explicit opt-in. Only real device evidence may promote a profile to hardware verified.

## Support

Use the **Sponsor** button on GitHub to support hardware testing, source recovery and new model adapters.

## Next

v0.6 builds the public static catalog/site and machine-readable distribution manifest. v1.0 follows only after additional legitimate voice/model coverage and real hardware verification.

VVH is independent community software and is not affiliated with robot-vacuum vendors or third-party character rights holders.
