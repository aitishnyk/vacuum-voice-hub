# Changelog

## 0.2.0 — 2026-10-08

### 50 Voice Wave
- expanded from 26 to **55 attributed voice variants**;
- catalog now spans **7 languages** and 13 explicit/18+ variants;
- added modern GitHub-hosted Dreame packs and legacy Roborock package sources;
- preserved 31 source-recovery records, including historical MD5/size metadata for old Russian Dreame archives.

### Compatibility Engine
- added semantic event catalog;
- added conservative `x10-known-v1` **106-event** hardware-verified profile;
- added coverage/core-coverage/missing/extra reports;
- X10 packaging now filters unverified extra event IDs;
- added optional fallback pack filling for missing target-model events.

### Tooling
- added `vvh stats`;
- added `vvh coverage`;
- added `--fallback` to build/install;
- added remote legacy Roborock `.pkg` source adapter;
- Web UI now shows source verification/origin layout and on-demand compatibility reports;
- 18+ packs are hidden by default in the Web UI.

### Attribution
- expanded credits and source verification metadata;
- historical dead/uncertain hosts remain recovery metadata rather than being presented as installable sources.

## 0.1.0 — 2026-10-08

- initial Vacuum Voice Hub product architecture;
- Xiaomi X10 / `dreame.vacuum.r2209` model adapter;
- 26 installable source variants with upstream attribution;
- 17-entry source-recovery backlog;
- RoboVoice, canonical Dreame OGG and Ijai named-MP3 source adapters;
- local MIoT installer;
- local Web UI and CLI;
- preview support;
- official Dreame stock-manifest discovery/restore commands;
- archive safety and source integrity verification;
- GitHub CI and contributor documentation.
