# Tested hardware

## Xiaomi Robot Vacuum X10 / `dreame.vacuum.r2209` — HARDWARE VERIFIED

Physical VVH test evidence:

- firmware: `4.3.9_1321`;
- MIoT Set Voice `siid=7 / piid=4`: accepted;
- robot fetched the generated package from the local HTTP server;
- voice package ID changed;
- state transitioned to `success`;
- progress reached `100`.

This remains the **only** model currently marked `device_tested=true`.

## v0.8 software target matrix

VVH now contains **109 model profiles**. The other 108 profiles are not silently promoted to physical verification.

Their evidence levels may be:

- model-specific protocol/spec evidence;
- community transport evidence;
- conservative family-derived event profile;
- package-format evidence;
- portable build-only semantic profile;
- vendor-signed-only restriction.

A model being present in the catalog means VVH can identify it and apply its declared compatibility/build policy. It does not by itself mean a custom voice has been installed on a physical example.

## Community verification

Use:

```bash
vvh report --ip ROBOT_IP --model MODEL_ID --credential ROBOT_CREDENTIAL
```

The report intentionally omits token, IP and MAC.

A maintainer should promote a model to hardware verified only after reviewing evidence for the exact model and transport. See [COMMUNITY_VERIFICATION.md](COMMUNITY_VERIFICATION.md).

## Signed Roborock generations

Newer Roborock generations that require vendor-signed voice packages remain explicitly blocked for arbitrary custom-package installation. A model cannot become “custom-install verified” merely because official voice packages are available.

## Safety rule

Similar model names, shared hardware families, Mi Home plugin availability, translated plugin UI, or unlocked official voice lists are useful research evidence but are **not** substitutes for a successful exact-device custom voice installation.
