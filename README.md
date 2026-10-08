# Vacuum Voice Hub

[![CI](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)

**Credits-first multi-model voice-pack platform for robot vacuums.**

Vacuum Voice Hub combines a source-attributed community catalog, semantic compatibility engine, model adapters and a local Creator Studio.

## v0.4

- **55 attributed community voice variants**
- **7 robot model profiles**
- **560+ observed event IDs**
- semantic namespace `vvh.semantic.v1`
- category-specific fallback
- transport evidence/fail-closed installation policy
- **Creator Studio**
- open semantic pack format **`vvh.voicepack.v1`**
- CLI + local Web UI

### Creator Studio

```bash
vvh web
```

Open `http://127.0.0.1:8787/creator`.

Or use the CLI:

```bash
vvh creator new --id my-pack --name "My Pack" --author "Me" --language en --license CC-BY-4.0
vvh creator events --model dreame.vacuum.r2209 --category cleaning
vvh creator validate ~/path/to/my-pack
vvh creator build ~/path/to/my-pack --model dreame.vacuum.r2209
```

One semantic pack can be built for multiple supported model profiles without renaming audio files to vendor-specific numeric IDs.

Read [Creator Studio documentation](docs/CREATOR_STUDIO.md).

## Model profiles

- Xiaomi X10 `dreame.vacuum.r2209` — **VVH hardware verified**
- Dreame D9 `p2009` — build/coverage only
- Dreame D10S Plus `r2240` — MIoT-spec transport
- Dreame L10S Ultra `r2228o` — MIoT-spec transport
- Dreame L40 Ultra `r2492*` — community device research
- Dreame X40 Ultra `r2416*/r2449*` — experimental transport
- MOVA P10 Pro Ultra `r2491*` — provisional profile / experimental transport

See [MODEL_MATRIX.md](docs/MODEL_MATRIX.md).

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
vvh doctor
vvh stats
vvh web
```

## Existing community voices

```bash
vvh list --language ru
vvh coverage warcraft --model dreame.vacuum.r2228o
vvh build warcraft --model dreame.vacuum.r2228o --fallback-category error=q0-russian
```

## Safety

VVH never upgrades a model to hardware verified by similarity alone. Unsupported local transports fail closed; experimental transports require an explicit override. Local robot tokens are not printed.

Creator Studio binds to localhost, uses ephemeral write authorization, rejects path traversal, bounds uploads and never publishes author audio automatically.

## Credits

Every catalog entry retains upstream source/credit metadata. Third-party character audio is source-linked rather than mirrored unless redistribution rights are clear.

- [Catalog](catalog/CATALOG.md)
- [Credits](CREDITS.md)
- [Third-party audio policy](THIRD_PARTY_AUDIO.md)

## Support

Use the **Sponsor** button on GitHub to support hardware testing, source recovery and new model adapters.

## Next

v0.5 adds a desktop shell, privacy-safe diagnostics, local install history and structured community compatibility reporting.

VVH is independent community software and is not affiliated with robot-vacuum vendors or third-party character rights holders.
