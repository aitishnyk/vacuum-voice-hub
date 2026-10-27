# Real capture notes — 2026-10-27

These are real browser captures of the local running v2.1 source, not mockups.

- home.png — running app Home.
- creator-demo.png — independent copied demo project in Creator Studio.
- waveform.png — real processed waveform and media players.
- model-library.png — generated canonical model library, searching r2209.
- universal-qa.png — Creator Universal Studio inspecting the copied X10 demo.
- export.png — real completed demo package with hash and download link.

Capture with the app's local HTTP server (`vvh web --port 8787`), then Home →
Try Demo → Process → Build → Continue in Creator Studio. The public catalog
is built with `vvh site build --output public`, served locally, then searched.
Use a fresh test-only VVH_DATA_DIR. Do not expose tokens, IP/MAC identifiers,
private projects or absolute user paths. Screen data uses bundled CC0 examples.
Browser playback reached readyState 4 and a progressing nonpaused media clock;
this is browser playback evidence, not certification of native audio output.
