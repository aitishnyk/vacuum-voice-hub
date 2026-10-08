# Tested hardware

## Xiaomi Robot Vacuum X10 / `dreame.vacuum.r2209` — HARDWARE VERIFIED

Physical test evidence:

- firmware: `4.3.9_1321`;
- MIoT Set Voice `siid=7 / piid=4`: `code=0`;
- robot fetched the generated package from the local HTTP server;
- `voice-packet-id` changed;
- state transitioned `downloading → success`;
- progress reached `100`.

This is the only model currently marked `device_tested=true`.

## Other v0.3 profiles

D9, D10S Plus, L10S Ultra, L40 Ultra, X40 Ultra and MOVA P10 Pro Ultra have source-backed event profiles, but **VVH has not physically installed a voice on those devices yet**.

See [MODEL_MATRIX.md](MODEL_MATRIX.md) for the exact evidence and install policy. Community reports must never contain local token, LAN IP or MAC address.
