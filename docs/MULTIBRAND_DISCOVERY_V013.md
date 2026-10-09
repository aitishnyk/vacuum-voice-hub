# v0.13.0 — Multi-Brand Device Discovery and Voice Compatibility

## Implementation

The cumulative catalog grows from **154 → 215 exact canonical device IDs** through **61 source-backed, identity-only additions**:

| Family | Newly listed profiles | Source |
|---|---:|---|
| Viomi | 26 | [MIoT Viomi listing](https://home.miot-spec.com/s/viomi.vacuum) |
| Xiaomi / Mijia | 19 | [MIoT Xiaomi listing](https://home.miot-spec.com/s/xiaomi.vacuum) |
| Roborock | 9 | [MIoT Roborock listing](https://home.miot-spec.com/s/roborock.vacuum) |
| ROIDMI | 4 | [MIoT ROIDMI listing](https://home.miot-spec.com/s/roidmi.vacuum) |
| IJAI | 3 | [MIoT IJAI listing](https://home.miot-spec.com/s/ijai) |

These are publicly indexed **device identities**. They do **not** imply that arbitrary voice packs are supported, that manufacturer signatures can be bypassed, or that voice transports have been tested. The 61 new profiles use the `semantic_bundle` research converter; every one has `transport.kind=unsupported-local`, `allow_default=false`, `device_tested=false`. Any attempt to enable new custom-voice transport through an experimental CLI flag is rejected.

All 154 earlier canonical models and their aliases are frozen in `tests/fixtures/v012_model_identity.json`. The historical 109-ID baseline still passes independently. No existing adapter/transport/hardware-test flag changes. All **55** existing source-attributed voice variants remain unchanged. The matrix of **215 × 55 = 11,825 software target combinations** means *coverage/build/preview eligibility*, not 11,825 physically validated installations.

## Research tool

```bash
vvh models --search "Qrevo"
vvh models --vendor Viomi
vvh model-info roborock.vacuum.a75
vvh model-compare roborock.vacuum.a75 viomi.vacuum.v60
vvh model-compare xiaomi.vacuum.d101 xiaomi.vacuum.ov51gl
```

The new `vvh.model-comparison.v1` report shows conservative event ID intersection, left/right percentage overlap, target format/adapter and source-attributed transport state, while **always** returning `custom_install_compatibility_proved=false` and `install_authorized_by_comparison=false`. Shared event IDs do not establish signing compatibility, firmware support, proprietary package structure or local upload API availability.

## Newly added canonical models

All entries below: source-backed identity, portable research-only package, install **blocked**, no invented Mi Home product/plugin numbers.

| Brand | Model | Exact MIoT ID |
|---|---|---|
| Viomi | Viomi Master 10 Max | `viomi.vacuum.v60` |
| Viomi | Viomi V3 Absolut | `viomi.vacuum.v56` |
| Viomi | Viomi Alpha 2 Lite | `viomi.vacuum.v53` |
| Viomi | Viomi V5 | `viomi.vacuum.v36` |
| Viomi | Viomi V5 Pro | `viomi.vacuum.v38` |
| Viomi | Viomi Alpha 2 Max | `viomi.vacuum.v41` |
| Viomi | Viomi Alpha 2 Pro (WH) | `viomi.vacuum.v40` |
| Viomi | Viomi V2 Max | `viomi.vacuum.v35` |
| Viomi | Viomi Alpha 2 Pro | `viomi.vacuum.v22` |
| Viomi | Viomi Alpha Lite | `viomi.vacuum.v37` |
| Viomi | Viomi 5G IoT Lingli 2 | `viomi.vacuum.v24` |
| Viomi | Viomi Alpha 2 Plus | `viomi.vacuum.v27` |
| Viomi | Viomi X3 | `viomi.vacuum.v25` |
| Viomi | Viomi Eagle | `viomi.vacuum.v29` |
| Viomi | Viomi Lingli UV | `viomi.vacuum.v20` |
| Viomi | Viomi Alpha UV | `viomi.vacuum.v21` |
| Viomi | Viomi S9 | `viomi.vacuum.v18` |
| Viomi | Mi Robot Vacuum-Mop P (Taiwan) | `viomi.vacuum.v9` |
| Viomi | Mi Robot Vacuum-Mop P (India) | `viomi.vacuum.v10` |
| Viomi | Viomi SE | `viomi.vacuum.v19` |
| Viomi | Viomi Dust-Collection Robot Vacuum | `viomi.vacuum.v17` |
| Viomi | Viomi V3 | `viomi.vacuum.v13` |
| Viomi | Viomi X2 (LDS) | `viomi.vacuum.v12` |
| Viomi | Viomi Vision Robot Vacuum | `viomi.vacuum.v11` |
| Viomi | Viomi Robot Vacuum Pro | `viomi.vacuum.v3` |
| Viomi | Viomi V2 Pro (export) | `viomi.vacuum.v6` |
| Xiaomi / Mijia | Mijia Robot Vacuum 4 (China) | `xiaomi.vacuum.ov81cn` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum H50 Pro | `xiaomi.vacuum.ov42gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum H50 | `xiaomi.vacuum.ov43gb` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum 5 Pro | `xiaomi.vacuum.ov21gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum 5 | `xiaomi.vacuum.ov31gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum S40 Pro | `xiaomi.vacuum.ov71gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum S40 | `xiaomi.vacuum.ov81gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum S40C | `xiaomi.vacuum.e101gb` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum H40 (Global) | `xiaomi.vacuum.ov51gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum X20 Max | `xiaomi.vacuum.d109gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum X20 Pro | `xiaomi.vacuum.d102gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum S20+ | `xiaomi.vacuum.b108gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum S20 | `xiaomi.vacuum.d106gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum E5 | `xiaomi.vacuum.c108` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum X20 | `xiaomi.vacuum.c101eu` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum S12 | `xiaomi.vacuum.b106eu` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum E12 | `xiaomi.vacuum.b112gl` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum E10C | `xiaomi.vacuum.b112bk` |
| Xiaomi / Mijia | Xiaomi Robot Vacuum E10 | `xiaomi.vacuum.b112` |
| Roborock | Roborock Q5 Pro | `roborock.vacuum.a72` |
| Roborock | Roborock Q8 Max | `roborock.vacuum.a73` |
| Roborock | Roborock Qrevo | `roborock.vacuum.a75` |
| Roborock | Roborock P10 | `roborock.vacuum.a74` |
| Roborock | Roborock G10S Pure | `roborock.vacuum.a64` |
| Roborock | Roborock G10S Auto | `roborock.vacuum.a76` |
| Roborock | Roborock Q5 | `roborock.vacuum.a34` |
| Roborock | Roborock G10 (A30) | `roborock.vacuum.a30` |
| Roborock | Roborock T8 | `roborock.vacuum.a37` |
| ROIDMI | ROIDMI EVE ROOK | `roidmi.vacuum.v63` |
| ROIDMI | ROIDMI EVE MAX | `roidmi.vacuum.sdj60` |
| ROIDMI | ROIDMI EVE CC | `roidmi.vacuum.v62` |
| ROIDMI | ROIDMI EVE (R1B) | `roidmi.vacuum.r1b` |
| IJAI / Xiaomi | Xiaomi Robot Vacuum-Mop 2 Pro (India) | `ijai.vacuum.v15` |
| IJAI / Xiaomi | Xiaomi Robot Vacuum-Mop 2i | `ijai.vacuum.v16` |
| IJAI / Xiaomi | Xiaomi Robot Vacuum S10 | `ijai.vacuum.v17` |

## Release and QA requirements

```bash
python -m pytest -q
python scripts/model_matrix_audit.py
python -m vacuum_voice_hub model-compare roborock.vacuum.a75 viomi.vacuum.v60
python -m vacuum_voice_hub release build --output release
python -m vacuum_voice_hub release verify release
```

The public catalog surfaces identity-provenance links for the newly added models while keeping language text templates separate from existing credited audio variants.

**Unverified external work:** custom voice installation on H40/H50/S40, ROIDMI EVA/MAX/CC, Viomi, Qrevo and modern Roborock requires exact-device+firmware package acceptance, signing/rollback research and lawful sample packages. No new physical acceptance is claimed by this release. Xiaomi X10 remains VVH's only hardware-tested target.
