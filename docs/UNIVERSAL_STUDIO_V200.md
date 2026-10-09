# v2.0 — Universal Voice Studio (offline software)

**Universal** refers to the shared, model-aware Creator/quality-control
interface; it does **not** mean universally supported firmware or that
all researched vacuum models have verified custom-voice installation.

The `vvh studio` CLI composes existing, tested source engines into one
privacy-conscious read-only model and recording audit.

```bash
vvh studio capabilities
vvh studio inspect --workspace ./my-creator-voice \
  --model dreame.vacuum.r2209 --language uk
vvh studio inspect --workspace ./my-creator-voice \
  --model dreame.vacuum.r2209 --language uk \
  --adapter ./my-adapter.json --translation-review ./uk-review.json
vvh studio report --workspace ./my-creator-voice \
  --model dreame.vacuum.r2209 --language uk \
  --audio-qa --output ./studio-review.json
```

The Studio inspection combines actual catalog identity, source manifest
and audio SHA-256, preflighted model event mapping/collisions, text-vs-audio
language coverage, offline build readiness and human review claims.
Optional inputs include an existing `vvh.adapter-descriptor.v1`,
`vvh.language-review.v1` checklist and local recording review with
an optional exact translation overlay. The Studio report is exclusive-new
JSON and never changes the Creator project.

`offline_pack_build_ready` means a locally mapped audio package can
be built; it is **not a device installation pass**, copyright license,
firmware/signature validation or evidence that any voice is in the
requested language. Human approvals remain claims requiring independent
validation. The model registry's 223 entries are researched identities,
55 voice variants are attributed historic assets, and >=22 script locales
contain **text**, not 22 prerecorded languages.

The repository preserves and composes the v1.2–v1.9 features: offline
translation QA and audio A/B, pronunciation lexicons, firmware matrix,
visual editing, local research inbox, third-party interchange, local
voice library and safe Creator recovery. All functions remain opt-in
and no new remote service, payment, Bunny storage, Telegram bot,
manufacturer override or unrestricted install transport is introduced.

See [migration](MIGRATION_V200.md) for backwards compatibility.
