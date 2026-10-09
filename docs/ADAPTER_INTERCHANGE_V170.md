# v1.7 — Offline Adapter Interchange SDK

`vvh adapter` creates a deterministic, portable research archive
containing **your own local audio** with exact model-specific semantic
event mappings. This is not an official vendor firmware package,
a signed installer, a remotely executed plugin, or a robot controller.

Create a local descriptor:

```json
{
  "schema": "vvh.adapter-descriptor.v1",
  "adapter_id": "community-sample",
  "model_id": "dreame.vacuum.r2209",
  "author": "Contributor",
  "license": "UNLICENSED",
  "entries": [
    {"semantic": "clean.start", "archive_name": "clean-start.wav"},
    {"semantic": "clean.pause", "archive_name": "clean-pause.wav"}
  ]
}
```

The Creator workspace must already assign matching audio for all entries.

```bash
vvh adapter preflight --workspace ./creator-voice --descriptor ./descriptor.json
vvh adapter build --workspace ./creator-voice --descriptor ./descriptor.json \
  --output ./research-interchange.zip
vvh adapter verify ./research-interchange.zip
```

Validation rejects aliases, unmapped/overlapping events, duplicate
portable filenames, path traversal and symlinked audio. Every archive
member uses the exact source encoding; renaming MP3 to WAV is refused.
There are limits of 128 events, 25 MiB per clip, 100 MiB total. ZIP
member timestamps/permissions/order are canonical for reproducibility.
The archive contains a manifest recording descriptor SHA-256, Creator
manifest SHA-256, model event IDs, audio hashes, origin authorship
and declared license. Verification rechecks every embedded clip.

All outputs are exclusively created new files. Audio is never changed,
uploaded or installed on a robot; third-party executable code is not
loaded. Distribution rights are **not** established by a user-declared
license, especially `UNLICENSED`. Nor does archive verification prove
real-device compatibility, package signing, local language fluency
or manufacturer permission. Only Xiaomi X10 is independently
hardware-tested by the VVH project.
