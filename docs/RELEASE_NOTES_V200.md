# Vacuum Voice Hub v2.0.0 — Universal Voice Studio Source Stable

A major open-source **offline software** release integrating the
working v1.2–v1.9 Creator and research toolchain behind a new
read-only `vvh studio` quality-control interface.

## Working features

- Source SHA-256 checks, model event mapping and core coverage.
- Local language script coverage, existing contributor translation
  review and optional recording review integrity.
- User-owned and bounded offline TTS, audio mastering, waveform,
  adapter interchange, community research and library workflows.
- Deterministic, checksum-verified Creator backups and recovery.
- `vvh studio capabilities`, `inspect` and copy-on-write `report`
  to inspect real models/workspaces without changing them.
- Preservation audits covering legacy model IDs/aliases, variants,
  script locales and no-transport-promotion policy.

## Strict boundaries

**v2.0 does not certify 223 models for custom-voice installation.**
Xiaomi X10 is the sole VVH physical custom-install verified device.
Other devices need independent, community-first model+firmware testing.
22+ script locales are text, not automatically recorded multilingual
voices. No manufacturer licensing, volunteer copyright/rights approval,
or signed/notarized desktop binary is asserted without actual evidence.

The official public release ZIP contains generated catalog/source
metadata only; it does not bundle copyrighted prerecorded content,
proprietary firmware, robot credentials or private local backups.

Migration requires no destructive conversion of prior Creator pack
schemas. See `docs/MIGRATION_V200.md` and
`docs/UNIVERSAL_STUDIO_V200.md`.
