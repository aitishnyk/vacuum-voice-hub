# Project status — v0.2.0 SEALED

- Product: **Vacuum Voice Hub**
- Repository: `aitishnyk/vacuum-voice-hub`
- Release: **v0.2.0**
- Source release state: **SEALED**
- Functional release merge: **PR #1**
- Functional release merge SHA: `e0e9e207ea33045673e7cbf8306e3936798b76fc`
- Catalog: **55 voice variants**
- Languages: **7**
- Explicit/adult variants: **13**
- Research/source-recovery records: **31**
- Physically verified model: **1** (`dreame.vacuum.r2209` / Xiaomi Robot Vacuum X10)
- X10 event profile: **106 conservative hardware-verified event IDs**
- Source adapters: Dreame numeric OGG, RoboVoice r2567r MP3, Ijai named MP3, remote Roborock `.pkg`, local named-audio import
- Compatibility Engine: coverage, core coverage, missing/extra IDs, grades
- Fallback builder: **enabled**
- Local Web UI: catalog, credits, preview, coverage, fallback, install, stock restore
- CLI: list/stats/info/coverage/build/install/preview/detect/import-pack/stock/restore-stock/web/research

## Release gates

The v0.2.0 functional payload was merged only after all release-branch gates were green.

Post-merge validation on `main`:

- GitHub Actions CI run `37732083393`: **SUCCESS**
- Python tests: **12/12 PASS**
- Editable package install with runtime dependencies: **PASS**
- Python compile: **PASS**
- CLI smoke: **PASS**
- `vvh --version`: **0.2.0**
- `vvh stats`: **55 voices**
- macOS installer shell syntax: **PASS**
- Web UI JavaScript syntax: **PASS**
- CodeQL Python analysis: **PASS**
- CodeQL Actions analysis: **PASS**
- Dependency graph update: **PASS**

No test skips remain in the release gate.

## Physical X10 evidence

On a real `dreame.vacuum.r2209`, firmware `4.3.9_1321`:

- `siid=7 / piid=4` Set Voice returned `code=0`;
- the robot fetched the generated package over LAN;
- `voice-packet-id` changed to a custom ID;
- state transitioned `downloading → success`;
- progress reached `100`.

The 106-event profile is intentionally conservative. Newer packs may contain hundreds of extra numeric IDs; v0.2 reports but omits those extras from X10 output until they are explicitly verified.

## Scope truth

- X10 transport/package acceptance is hardware verified.
- The catalog contains many upstream community packs that are **convertible**, not individually hardware-certified on X10.
- Historical dead/uncertain hosts remain recovery metadata and are not falsely exposed as installable artifacts.
- Third-party character audio remains upstream/source-linked rather than mirrored by VVH by default.
- GitHub Releases/tag publication is separate from source sealing; the connected GitHub automation currently has read-only access to release endpoints.

## Next roadmap target

**v0.3 — Multi-model Hardware Wave**

- explicit event profiles for additional Dreame/Xiaomi models;
- physical verification on at least 3 more robot models;
- Roborock family adapters;
- Mova / Trouver adapters;
- model-specific donor/fallback workflows;
- community “Works on my robot” compatibility reports.
