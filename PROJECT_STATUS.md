# Project status — v0.1.0

- Product name: **Vacuum Voice Hub**
- Planned GitHub slug: `vacuum-voice-hub`
- Planned owner/repo: `aitishnyk/vacuum-voice-hub`
- Installable source variants in catalog: **26**
- Explicit/adult variants: **7**
- Research/source-recovery backlog: **17**
- Physically verified model: **1** (`dreame.vacuum.r2209` / Xiaomi Robot Vacuum X10)
- Source format adapters: **4** (Dreame canonical OGG, RoboVoice r2567r MP3, Ijai named MP3, old Roborock named audio)
- Local legacy importer: `.pkg`, `.zip`, `.tar.gz`, directories
- Local web UI: catalog, source credits, preview, install, official stock restore
- CLI: list/info/build/install/preview/detect/import-pack/stock/restore-stock/web/research
- Tests: **7/7 PASS**
- Python compile check: PASS
- Bash syntax check: PASS
- Web UI JavaScript syntax check: PASS

## Physical X10 evidence

On a real `dreame.vacuum.r2209`, firmware `4.3.9_1321`:

- `siid=7 / piid=4` Set Voice returned `code=0`;
- the robot fetched the generated package from the Mac over LAN via HTTP 200;
- `voice-packet-id` changed to a custom ID;
- state transitioned `downloading` → `success`;
- progress reached `100`.

This verifies the transport/package pipeline. Individual third-party voice sources remain marked `convertible` until separately tested on hardware.

## GitHub publishing status

The repository is published at `aitishnyk/vacuum-voice-hub`.
The complete v0.1.0 source tree is present on `main`.

Repository visibility is checked separately from the source release; for an open-source launch it should be **Public**.
