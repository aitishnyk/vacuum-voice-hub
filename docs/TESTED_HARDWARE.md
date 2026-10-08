# Tested hardware

## Xiaomi Robot Vacuum X10 / `dreame.vacuum.r2209`

Physical test evidence supplied by a project user:

- firmware: `4.3.9_1321`
- MIoT Set Voice `siid=7 / piid=4`: `code=0`
- robot fetched generated package over LAN via HTTP 200
- `voice-packet-id` changed to custom ID
- state transitioned `downloading` → `success`
- progress reached `100`

This verifies the **transport/package pipeline**, not every third-party voice source in the catalog. Each pack remains `convertible` until separately exercised.
