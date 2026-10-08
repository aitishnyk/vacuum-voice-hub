# Project status — v0.2.0 candidate

- Product: **Vacuum Voice Hub**
- Repository: `aitishnyk/vacuum-voice-hub`
- Catalog: **55 voice variants**
- Languages: **7**
- Explicit/adult variants: **13**
- Research/source-recovery records: **31**
- Physically verified model: **1** (`dreame.vacuum.r2209` / Xiaomi Robot Vacuum X10)
- X10 event profile: **106 conservative hardware-verified event IDs**
- Source adapters: Dreame numeric OGG, RoboVoice r2567r MP3, Ijai named MP3, remote Roborock `.pkg`, local named-audio import
- Compatibility Engine: coverage, core coverage, missing/extra IDs, grades
- Fallback builder: enabled
- Local Web UI: catalog, credits, preview, coverage, fallback, install, stock restore
- CLI: list/stats/info/coverage/build/install/preview/detect/import-pack/stock/restore-stock/web/research

## Physical X10 evidence

On a real `dreame.vacuum.r2209`, firmware `4.3.9_1321`:

- `siid=7 / piid=4` Set Voice returned `code=0`;
- the robot fetched the generated package over LAN;
- `voice-packet-id` changed to a custom ID;
- state transitioned `downloading → success`;
- progress reached `100`.

The 106-event profile is intentionally conservative. Newer packs may contain hundreds of extra numeric IDs; v0.2 reports but omits those extras from X10 output until they are explicitly verified.

## Release gate

v0.2 is ready to merge only after:
- all automated tests pass;
- package-data mirrors are exact;
- source metadata policy passes;
- Web UI/CLI compile checks pass;
- GitHub Actions is green on the release branch.
