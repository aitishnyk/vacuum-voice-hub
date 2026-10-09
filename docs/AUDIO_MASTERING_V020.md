# Offline Audio Mastering — v0.20

The optional non-destructive mastering preview takes a **local** WAV/MP3/OGG/FLAC/M4A/AAC/Opus recording, bounded-decodes it to mono 16 kHz/16-bit PCM, trims outer silence, preserves configurable padding, applies a bounded peak gain and short fades, and writes a **new WAV file only**.

```bash
vvh creator master-preview ./recording.ogg \
  --output ./previews/recording-master.wav \
  --target-peak-dbfs -4 \
  --silence-dbfs -45 \
  --padding-ms 80 \
  --fade-ms 8
```

Use `--no-trim-silence` when a particular prompt requires its original leading and trailing pauses. The command refuses existing output paths, original-source overwrites, silent or overquiet material, invalid finite limits, sources above the existing 25 MiB / 180-second constraints, and clips shorter than 0.25 seconds after trimming. A fixed 12 dB maximum automatic gain prevents extremely quiet recordings being boosted into noisy output. All processing is local; existing Creator workspaces and source files remain unchanged.

Reports include SHA-256 hashes, original/processed QA, removed sample counts and explicit `human_review_required=true`, `redistribution_verified=false`, `install_authorized=false`. They are **previews**, not published pack versions. Review by listening, check model-event mapping and rights, then explicitly assign the chosen resulting WAV to a Creator project.

This does not do de-noising, voice conversion, automatic mastering to perceived LUFS or device installation. Such features must be independently evaluated before they can be described as supported.
