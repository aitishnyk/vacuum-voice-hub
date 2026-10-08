# Model compatibility matrix — v0.3

VVH separates **format/profile support** from **physical installation verification**.

| Model | IDs / aliases | Event profile | Events | Local install policy | Evidence |
|---|---|---|---:|---|---|
| Xiaomi Robot Vacuum X10 | `dreame.vacuum.r2209` | `x10-known-v1` | 106 | **Hardware verified** | Physical VVH test: code=0, robot HTTP GET, success/100% |
| Dreame D9 | `dreame.vacuum.p2009` | `d9-community-v1` | 188 | **Build / coverage only** | ccoors/czaky classic Dreame format; no verified local set-voice property |
| Dreame D10S Plus | `dreame.vacuum.r2240` | `d10s-plus-community-v1` | 111 | MIoT-spec supported, device verification pending | Official MIoT audio service 7 / voice-change piid 4 + D10S community pack |
| Dreame L10S Ultra | `dreame.vacuum.r2228o` | `l10s-ultra-extracted-v1` | 182 | MIoT-spec supported, device verification pending | MIoT spec + device-extracted sound list / upstream packs |
| Dreame L40 Ultra | `r2492a/b/j` | `l40-ultra-community-v1` | 470 | Community device research, device verification pending | jan-hinter-droid documents working VOICE_CHANGE siid 7 / piid 4 |
| Dreame X40 Ultra | `r2416a/c`, `r2449a/k`, `r2416` | `x40-ultra-extracted-v1` | 514 | **Experimental opt-in** | X40 pack/event extraction; transport family-inferred |
| MOVA P10 Pro Ultra | `mova/dreame.r2491*` | `mova-p10-pro-ultra-provisional-v1` | 425 | **Experimental opt-in** | Valetudo hardware-family evidence; conservative L40∩X40 event set |

## Status vocabulary

- **Hardware verified** — a VVH installation log from a physical robot confirms download and activation.
- **MIoT-spec** — the model's published MIoT service exposes the required voice property, but VVH still needs a physical report.
- **Community device research** — another project demonstrates the exact voice-change path on that model family.
- **Experimental** — a plausible family transport exists but VVH refuses to use it without explicit opt-in.
- **Build / coverage only** — VVH can adapt packs and compute coverage, but intentionally refuses local installation.

Never upgrade a model to hardware verified from model similarity alone.
