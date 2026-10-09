# v1.5 — Visual Timeline & Non-destructive Audio Cutting

In the local Creator Studio (`vvh desktop` / `vvh web`), the new
**Audio Timeline** panel lets you select a local recording, see its waveform,
enter precise start/end positions and fade duration, and export a NEW
16 kHz mono PCM WAV, without assigning it to a robot or editing the
original. Browser decodes locally with Web Audio; supported source
codecs depend on the browser. Limits: 25 MiB, 0.25–180 seconds,
mono/stereo, selected duration at least 0.25 seconds.
No recording data is sent to the server by the timeline interface.

Deterministic CLI version:
```bash
vvh creator waveform ./licensed-recording.wav --bins 256
vvh creator cut-preview ./licensed-recording.wav --start-ms 250 \
  --end-ms 1250 --fade-ms 8 --output ./new-review-preview.wav
vvh creator audio-compare ./licensed-recording.wav ./new-review-preview.wav
```

Python decoding uses the existing bounded local FFmpeg pipeline,
16 kHz mono WAV, exclusive new output and source SHA-256 check.
Cuts are for human listening and optional later explicit Creator
assignment — a trimmed recording is **never auto-approved, auto-installed
or uploaded**, and its distribution rights are not inferred. Users
still need adequate noise control and human pronunciation review;
this stage is not a professional LUFS/true-peak/noise-reduction DAW.
