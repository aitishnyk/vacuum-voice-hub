# v1.8 — Local Attributed Voice Library

The Library is a **private offline index of your own Creator workspaces**,
not a public repository of vendor voice files. It stores voicepack identity,
title, language, author, *declared* license, per-pack manifest SHA-256,
aggregate audio SHA-256 fingerprint and event counts. No actual recordings,
file paths, source filenames, robot credentials or web URLs are included.

```bash
vvh library index --workspace ./voices/uk-example \
  --workspace ./voices/en-example --output ./my-voice-library.json
vvh library search ./my-voice-library.json --language uk
vvh library search ./my-voice-library.json --query "Contributor"
vvh library search ./my-voice-library.json --license CC-BY-4.0
vvh library audit ./my-voice-library.json
vvh library reconcile ./my-voice-library.json \
  --workspace ./voices/uk-example --workspace ./voices/en-example
```

The index refuses duplicate IDs, symlink workspaces/recordings, invalid
Creator metadata, missing/empty audio and existing output files.
For each project it hashes the manifest and all assigned local recordings,
with 128 projects, 256 audio assignments per project, 25 MiB per clip and
256 MiB per-project limits. The resulting JSON has a self-checksum; this is
not a signature. Reconciliation requires the operator to supply the
original paths again; they were never embedded in the index.

**Important:** an author's license declaration is never proof of
copyright ownership, redistribution authorization, spoken-language
quality or installation compatibility. A self-created index and
`CC-BY-4.0` string do not automatically grant you those rights.
Only Xiaomi X10 has existing independent VVH custom voice install testing.
No remote upload, download, commercial entitlement or hosting occurs.
