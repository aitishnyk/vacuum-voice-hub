# v0.8 — Mass Model Expansion

Vacuum Voice Hub v0.8 imports the requested Mi Home ecosystem inventory and expands the target matrix from 7 to **109 model profiles**.

With 55 catalog voice variants, the software compatibility matrix now contains **5,995 voice × model target combinations**.

## What “optimized for a model” means

Every target model receives:

1. a declared model profile;
2. a bounded event set;
3. a target adapter;
4. a package/output format;
5. semantic coverage calculation;
6. model-aware filtering so unknown event IDs are not injected;
7. preview support;
8. Creator Studio target support;
9. an explicit install policy.

Direct local installation is a separate capability and is never inferred just from the ability to build a package.

## Target families

### Dreame numeric — 32 models

Output:
- numeric event filenames;
- Ogg Vorbis;
- 16 kHz mono;
- `tar.gz`.

Known/extracted models keep their model-specific event profiles.

Unverified modern Dreame-family models use `dreame-modern-conservative-v1`, the intersection of the verified/source-backed X10, D10S Plus and L10S Ultra event sets. This intentionally reduces coverage rather than inventing unsupported event IDs.

### Roborock legacy — 33 models

VVH maps canonical semantics back to classic Roborock prompt names such as:

- `start.wav`;
- `pause.wav`;
- `finish.wav`;
- `home.wav`;
- `charging.wav`;
- error prompts.

Old-generation export:
- PCM S16LE WAV;
- 16 kHz mono;
- tar/gzip payload;
- historical ccrypt `.pkg` wrapper.

The local MiIO install path uses `dnld_install_sound` and is still marked **experimental per exact model** until a VVH physical report is received.

Building encrypted Roborock `.pkg` currently requires the external `ccrypt` executable.

For newer Roborock generations whose voice packages require a vendor certificate/signature, VVH remains **official-signed-only** and will not pretend that arbitrary custom packages can be installed.

### IJAI — 8 models

Output:
- named `sound_*.mp3`;
- 16 kHz mono;
- ZIP.

For `ijai.vacuum.v2`, `v3`, `v18` and `v19`, community evidence documents the MIoT action form:
- service 14;
- action 1;
- language input;
- package URL input;
- MD5 input.

VVH exposes this path only as **experimental** until exact-device verification exists.

### Portable semantic — 36 models

For Xiaomi/Mijia/Viomi/ROIDMI/Smartmi ecosystem models where the custom vendor package layout or transport has not yet been established, VVH creates an explicit non-installable bundle:

- canonical semantic OGG files;
- model-safe core event filtering;
- manifest `vvh.portable-build.v1`;
- `installable=false`.

This is useful for Creator Studio, conversion research, source comparison and future adapter work without making an unsafe installation claim.

## Evidence hierarchy

From strongest to weakest:

1. **hardware-verified** — VVH physical robot evidence;
2. **spec/community transport** — published protocol evidence, exact VVH device test pending;
3. **experimental family transport** — plausible documented family path, explicit user opt-in required;
4. **official-signed-only** — arbitrary custom install blocked by vendor signing;
5. **build-only** — target/preview/coverage supported, custom install unknown.

As of v0.8, Xiaomi X10 remains the only hardware-verified model.

## Inventory provenance

The requested model/product/plugin rows were taken from the Mi Home plugin inventory supplied for this expansion and cross-referenced against public ecosystem research.

Important: Mi Home plugin availability, translated plugin UI or an “official voices unlocked” note is **not** equivalent to proof that arbitrary custom voice packs can be installed.

## Next adapter research

Highest-value build-only candidates for transport/package reverse engineering:

- ROIDMI EVA / EVE;
- Xiaomi H40;
- Xiaomi X20+;
- Mijia 5 / 5 Pro / 5C / 6 / 6 Pro / 6 Max;
- Viomi Alpha / V3 families;
- newer Dreame S10/X10/W10 families;
- additional IJAI models.

Promotion requires concrete package-layout and transport evidence, followed by privacy-safe physical verification.
