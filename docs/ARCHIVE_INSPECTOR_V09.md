# v0.9 Archive Inspector — Offline package inventory

`vacuum_voice_hub.archive_inspector.inspect_archive(path)` reads ZIP and tar-family archives locally and returns `vvh.archive-inventory.v1` with a per-file SHA-256, normalized archive path, byte count and audio-extension flag.

It never extracts entries, runs executables, contacts vendor servers, changes model profiles, or authorizes an installation. It cannot infer proprietary model compatibility or prove an archive is accepted by a robot.

Limits: 128 MiB input, 512 regular files, 16 MiB per file, 128 MiB total decompressed payload. Member size is checked before and during streaming. Paths with traversal/absolute components, case-collisions, special files, links and encrypted ZIP entries are rejected. This is an inventory/research primitive; format-specific adapter verification and real-device tests remain necessary.

Usage:

```python
from vacuum_voice_hub.archive_inspector import inspect_to_json
print(inspect_to_json("candidate-voice.zip"))
```

Tests: `python -m pytest -q tests/test_archive_inspector_v09.py`.
