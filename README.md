# Vacuum Voice Hub

[![CI](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)

**Credits-first multi-model voice-pack platform for robot vacuums.**

## v0.7 platform

- 55 attributed community voice variants
- 7 robot model profiles
- 560+ observed event IDs
- `vvh.semantic.v1` compatibility layer
- `vvh.voicepack.v1` Creator Studio format
- `vvh.compat-report.v1` privacy-safe device evidence
- `vvh.public-catalog.v1` deterministic public catalog
- `vvh.release-manifest.v1` reproducible release metadata
- `vvh.update-feed.v1` stable update-feed contract
- desktop shell + macOS/Windows/Linux packaging
- OS keyring support
- local secret-redacted install history
- SPDX SBOM + SHA-256 release verification

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

## Public catalog

```bash
vvh site build --output public
vvh site verify public
```

Read [PUBLIC_CATALOG.md](docs/PUBLIC_CATALOG.md).

## Reproducible release bundle

```bash
export SOURCE_DATE_EPOCH=1700000000
vvh release build --output release
vvh release verify release
```

The bundle contains the public catalog ZIP, SPDX SBOM, release manifest, update feed and SHA256SUMS.

Read [DISTRIBUTION.md](docs/DISTRIBUTION.md) and [SIGNING.md](docs/SIGNING.md).

## Model evidence

- Xiaomi X10 `dreame.vacuum.r2209` — **VVH hardware verified**
- Dreame D9 `p2009` — build/coverage only
- Dreame D10S Plus `r2240` — MIoT-spec transport
- Dreame L10S Ultra `r2228o` — MIoT-spec transport
- Dreame L40 Ultra `r2492*` — community device research
- Dreame X40 Ultra `r2416*/r2449*` — experimental transport
- MOVA P10 Pro Ultra `r2491*` — provisional / experimental

Physical verification is never inferred from similar hardware.

## Creator Studio

```bash
vvh creator new --id my-pack --name "My Pack" --author "Me" --language en --license CC-BY-4.0
vvh creator build ~/path/to/my-pack --model dreame.vacuum.r2209
```

Read [CREATOR_STUDIO.md](docs/CREATOR_STUDIO.md).

## Credentials / install

```bash
pip install -e ".[security]"
vvh credential save home-x10
vvh install maxim-full --model dreame.vacuum.r2209 --ip 192.168.1.123 --credential home-x10
```

## Community verification

```bash
vvh history --limit 20
vvh report --ip 192.168.1.123 --model dreame.vacuum.r2209 --credential home-x10
```

Reports omit token, IP and MAC and are never uploaded automatically.

## Signing claim boundary

CI-built binaries are **built**, not automatically signed/notarized. Ordinary release manifests are intentionally `unsigned`. Signing status changes only in a trusted signing environment with a verifiable key/signature.

## Credits

- [Catalog](catalog/CATALOG.md)
- [Credits](CREDITS.md)
- [Third-party audio policy](THIRD_PARTY_AUDIO.md)

## Support

Use the GitHub **Sponsor** button to support hardware testing, source recovery and adapters.

VVH is independent community software and is not affiliated with robot-vacuum vendors or third-party character rights holders.
