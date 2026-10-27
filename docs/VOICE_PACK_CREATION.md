# Voice pack creation

Create a unique Creator project with accurate language, author, source and
license metadata. Import only recordings you own or may use. Assign files to
semantic events; target adapters map these to actual model event IDs.

Supported input extensions: WAV, MP3, OGG, FLAC, M4A, AAC and Opus. Each imported
clip is limited to 25 MiB. PCM16 mono 16 kHz WAV is a reliable working format;
compressed QA and builds use bounded local FFmpeg where supported. The waveform
editor exports a new WAV; it does not silently replace a Creator assignment.

Choose the exact canonical model ID. Use Validate, Coverage, Preflight,
Audio QA and Universal Studio inspection. Listen to each event and complete
human language and rights review. Hashes show integrity, not legal ownership
or spoken-language accuracy. Fix missing required events before hardware use.

Build creates the adapter's actual package format. At least five mapped events
are necessary for the basic build gate; this minimum is not full coverage.
Review output content and coverage for the actual device. A portable semantic
ZIP is not equivalent to a vendor-specific installable package.

Back up using `vvh creator backup WORKSPACE --output NEW_BACKUP.zip` and
verify it with `vvh creator backup-verify NEW_BACKUP.zip`. Restore only into
a new destination using `vvh creator backup-restore NEW_BACKUP.zip --output-dir NEW_DIRECTORY`.
For command details use `vvh creator --help`.

Installing to a robot is a separate, explicitly credentialed action governed
by existing model policies. Demo workflows never invoke it.
