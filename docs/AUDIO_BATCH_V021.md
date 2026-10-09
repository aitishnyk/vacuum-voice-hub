# v0.21 offline audio production batch

For whole local voice collections, the batch-mastering command processes 1–256
**immediate local audio files** without touching source recordings:

```bash
vvh creator master-batch \
  --input-dir ./my-voice/audio \
  --output-dir ./mastered-previews \
  --max-files 64 \
  --target-peak-dbfs -6 --silence-dbfs -45 \
  --padding-ms 80 --fade-ms 8
```

The output directory must not exist. Sources may be WAV, OGG, MP3, FLAC,
M4A, AAC or Opus. Non-audio README/metadata files are ignored. Symlinked
audio inputs, conflicting names after converting to WAV (including
case-insensitive collisions), dangerous/invalid parameter values, too-quiet
or silent recordings, and unsupported formats are rejected. Every clip uses
the same bounded local decoder and mastering algorithm as v0.20; no cloud
API or robot network connection.

Only on complete success are the new WAV previews and
`batch-mastering.json` report kept. Any processing failure removes the
incomplete new output directory. The report lists source/output SHA-256,
individual signal QA and trims in deterministic order, while marking
`human_review_required=true`,
`creator_manifest_changed=false`,
`redistribution_verified=false`,
`install_authorized=false`.

Listen, verify exact language and model event mapping, review the rights,
and **explicitly assign** selected new WAVs through Creator Studio. This
is not automatic voice restoration, signature bypass, automatic publication
or hardware-compatibility certification.
