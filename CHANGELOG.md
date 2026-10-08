# Changelog

## 0.3.0 — 2026-10-08

### Multi-model Hardware Wave
- expanded model catalog from 1 to **7 profiles**;
- added D9, D10S Plus, L10S Ultra, L40 Ultra, X40 Ultra and MOVA P10 Pro Ultra;
- extracted/source-backed event profiles from 111 to 514 events;
- kept Xiaomi X10 as the only hardware-verified model.

### Semantic Compatibility Engine
- expanded semantic event union to **560+ observed IDs**;
- introduced `vvh.semantic.v1`;
- added category-level coverage;
- added semantic missing-core diagnostics;
- added category-specific fallback packs;
- extra/unverified event IDs remain filtered by each target profile.

### Transport safety
- model-level transport contracts;
- D9 local installation is build/coverage-only;
- X40 and MOVA transports require explicit experimental opt-in;
- D10S Plus/L10S Ultra use MIoT-spec evidence;
- L40 uses community device research evidence;
- robot HTTP download confirmation is tracked separately from Set Voice acceptance.

### UX / CLI
- multi-model Web UI;
- transport/evidence status panel;
- model-aware coverage labels;
- category fallback selectors;
- `vvh model-info`;
- `--fallback-category CATEGORY=VOICE`;
- `--allow-experimental-transport`.

## 0.2.0 — 2026-10-08

- 55 attributed voice variants across 7 languages;
- 106-event X10 compatibility profile;
- coverage/fallback engine;
- remote legacy Roborock `.pkg` support;
- source recovery and expanded CI gates.

## 0.1.0 — 2026-10-08

- initial X10-focused Vacuum Voice Hub foundation.
