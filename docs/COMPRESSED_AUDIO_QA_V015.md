# v0.15 — Compressed Audio QA & Actual Language-Audio Coverage

This release adds engineering-quality **offline source-audio inspection** and distinguishes multilingual **text readiness** from audio files truly assigned to the Creator workspace. No recording or proprietary vendor voice is downloaded.

## Read WAV, MP3, OGG, FLAC, M4A, AAC and Opus

The previous `vvh creator qa` inspected 16-bit PCM WAV only. v0.15 adds **explicit opt-in** bounded local FFmpeg decoding of common compressed formats:

```bash
vvh creator qa /path/to/workspace \
  --model dreame.vacuum.r2209 --decode-compressed
vvh creator preflight /path/to/workspace \
  --model viomi.vacuum.v60 --check-audio --decode-compressed
vvh creator batch /path/to/workspace \
  --model dreame.vacuum.r2209 --model viomi.vacuum.v60 \
  --output-dir /path/to/new-output --check-audio --decode-compressed
```

The analysis:
- accepts only approved local file extensions, with 25 MiB maximum input;
- uses FFmpeg with no standard input, restricted `file,pipe` protocols, mono 16 kHz 16-bit PCM output and a **45-second per-source timeout**;
- caps decoded output at ~6.5 MB and ~181 seconds; content hitting the 180-second practical limit is flagged as a truncated-duration risk, **not** labeled clean;
- analyzes temporary audio and deletes the temporary output afterwards;
- retains existing bounded WAV inspection and legacy default (non-WAV marked `not-analyzed` unless opt-in is requested);
- reports peak/RMS levels, clipping, silence, duration, warning flags, and whether decode happened.

These are signal heuristics. They **cannot prove** spoken-language correctness, pleasant timbre, absence of profanity, voice intellectual-property rights or actual robot-device compatibility.

## Export non-destructive gain-only WAV previews

```bash
vvh creator gain-preview ./voice.mp3 --gain-db -4.5 \
  --output ./preview-minus-4_5.wav
```

Gain preview accepts -12 to +12 dB and writes an **entirely new** 16-bit WAV; existing output paths or use of the original source path are refused. It returns SHA-256 and before/after quality reports, including clipping and silence warnings. It does **not** replace original audio, modify a Creator manifest, embed third-party speech, or claim the recording's distribution rights. Human listening and a separate selection/reimport step are still required.

## Per-language: text scripts are not audio

```bash
vvh creator language-coverage /path/to/workspace \
  --model dreame.vacuum.r2209 --language uk

vvh creator language-coverage /path/to/workspace \
  --model dreame.vacuum.r2209 --language uk \
  --overlay ./reviewed-uk-translations.json
```

The new report `vvh.language-audio-coverage.v1` shows:
- script events with translated text and the actual **assigned** audio filename semantics;
- target-model event IDs covered by text vs those with assigned audio;
- missing audio for script-ready events, and audio events with no corresponding supplied text;
- language code declared in the Creator manifest vs selected text locale;
- text coverage and **declared-language audio assignment** coverage as separate percentages;
- explicit negative claims: `speaker_language_verified=false`, `recording_license_verified=false`, `install_authorized=false`.

If a project declares Ukrainian audio but the user selects Russian text scripts, the report will not count those audio clips as confirmed for Russian. Matching metadata still **does not** mean the audio actually speaks that language: that requires human listening.

## Creator Studio

Start `vvh web` and open the localhost `/creator` page. Enable **Decode MP3/OGG/FLAC…** to opt in to compressed source inspection for Audio QA and Preflight, or **Decode compressed** for Batch. In the multilingual section click **Text vs Audio Coverage** to inspect the selected locale against actual Creator assignments. Web UI does not expose filesystem-wide gain editing; gain preview is CLI-only.

## Software and hardware invariants

- **215** existing model profiles and aliases, **55** source-linked voice variants and **18** text-only script locales remain unchanged.
- No new device transports, region-unlocks, firmware patches or signing bypass.
- **Xiaomi X10 remains the only physically verified VVH device**. A successful preview is not an approved install on the other 214 targets.
- Source release acceptance requires GitHub Actions CI, exact model-matrix and regression checks, CodeQL, Public Site, Release Bundle and macOS/Linux/Windows Desktop Packages.
- Do not redistribute a generated TTS voice without checking the separate model/recording license.
