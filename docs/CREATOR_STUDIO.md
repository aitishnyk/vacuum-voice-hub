# Creator Studio — vvh.voicepack.v1

Creator Studio is a local authoring environment for model-independent robot-vacuum voices.

As of v0.8 the model selector can target **109 profiles** across Dreame numeric, Roborock, IJAI and portable semantic adapter families.

## Core idea

Author semantic events once:

```text
clean.start
clean.pause
clean.complete
dock.return.charge
error.main_brush
```

VVH maps those semantics to the bounded event profile and target package adapter for the selected model.

The same semantic project can therefore be exported differently for different families without manually renaming the source audio.

## Workspace

```text
my-pack/
├── manifest.json
└── audio/
    ├── clean.start.wav
    ├── clean.pause.wav
    └── error.main_brush.ogg
```

The manifest schema remains `vvh.voicepack.v1`.

## Web Studio

```bash
vvh web
```

Open `http://127.0.0.1:8787/creator`.

The v0.8 UI includes target-model search.

## Target output

Depending on the selected model, Creator Studio may produce:

- Dreame numeric OGG `tar.gz`;
- classic Roborock encrypted `.pkg` (requires external `ccrypt`);
- IJAI named-MP3 ZIP;
- portable semantic OGG ZIP with `installable=false`.

A successful build is not automatically an installation claim. The model transport policy remains independent and fail-closed.

## Privacy

- server binds to `127.0.0.1`;
- Creator write/upload APIs require an ephemeral session;
- preview URLs are session protected;
- workspace paths reject traversal;
- uploaded author audio remains local;
- no Creator project is published to GitHub automatically.
