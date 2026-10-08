# Creator Studio — vvh.voicepack.v1

Creator Studio is a local authoring environment for model-independent robot-vacuum voices.

## Format

A workspace contains:

```text
my-pack/
├── manifest.json
└── audio/
    ├── clean.start.wav
    ├── clean.pause.wav
    └── error.main_brush.ogg
```

Minimal manifest:

```json
{
  "schema": "vvh.voicepack.v1",
  "id": "my-pack",
  "name": "My Pack",
  "author": "Your Name",
  "language": "en",
  "adult": false,
  "license": "CC-BY-4.0",
  "source_url": null,
  "description": null,
  "events": {
    "clean.start": "audio/clean.start.wav",
    "clean.pause": "audio/clean.pause.wav"
  }
}
```

The authoritative JSON Schema is [../schemas/vvh.voicepack.v1.schema.json](../schemas/vvh.voicepack.v1.schema.json).

## CLI

```bash
vvh creator new --id my-pack --name "My Pack" --author "Me" --language en --license CC-BY-4.0
vvh creator events --model dreame.vacuum.r2209 --category cleaning
vvh creator assign ~/.local/share/vacuum-voice-hub/creator/my-pack clean.start ./start.wav
vvh creator validate ~/.local/share/vacuum-voice-hub/creator/my-pack
vvh creator coverage ~/.local/share/vacuum-voice-hub/creator/my-pack --model dreame.vacuum.r2209
vvh creator build ~/.local/share/vacuum-voice-hub/creator/my-pack --model dreame.vacuum.r2209
```

On macOS, the default workspaces are under `~/Library/Application Support/VacuumVoiceHub/creator/`.

## Web Studio

Start:

```bash
vvh web
```

Then open:

```text
http://127.0.0.1:8787/creator
```

Creator Studio supports:
- creating workspaces;
- editing safe manifest metadata;
- selecting a target model;
- filtering semantic events;
- uploading WAV/MP3/OGG/M4A/AAC/FLAC/Opus per semantic event;
- local audio preview;
- validation;
- model coverage;
- model-specific build.

Uploads are limited to 25 MiB each and remain local.

## Security boundaries

- the server binds to `127.0.0.1`;
- write/upload Creator APIs require an ephemeral session token;
- preview URLs also require the session token;
- event paths cannot be absolute or contain `..`;
- workspace uploads never publish themselves to GitHub;
- Creator Studio does not claim redistribution rights for user-supplied audio.

## Semantic portability

A semantic event like `clean.start` can map to a different numeric ID set for each model profile. The creator writes the semantic intent once; VVH selects only IDs known to the target model.

Unknown or ambiguous events are not guessed.
