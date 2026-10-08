# Changelog

## 0.4.0 — 2026-10-08

### Creator Studio
- introduced the `vvh.voicepack.v1` semantic authoring format;
- added JSON Schema contract;
- added local creator workspaces;
- added `vvh creator new/list/validate/assign/remove/events/coverage/build`;
- added model-independent semantic audio assignment;
- added automatic WAV/MP3/OGG/etc. normalization to target OGG;
- added model-specific semantic build.

### Local Web Studio
- added `/creator`;
- workspace creation and metadata editing;
- event search/category filters;
- per-event audio upload and preview;
- validation and target-model coverage;
- one-click local package build.

### Security
- creator paths reject traversal/absolute paths;
- upload size is bounded to 25 MiB;
- creator write APIs use ephemeral session authorization;
- creator preview URLs are session protected;
- author audio stays local by default.

## 0.3.0 — 2026-10-08
- seven model profiles;
- 560+ observed event IDs;
- semantic category fallback;
- model transport evidence policy;
- multi-model Web UI.

## 0.2.0 — 2026-10-08
- 55 attributed voice variants;
- X10 compatibility engine and fallback.

## 0.1.0 — 2026-10-08
- initial X10-focused foundation.
