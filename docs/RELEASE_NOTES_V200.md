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

## v2.0 release acceptance and publication evidence

The exact integrated source on main commit
[`419ca0033874b11ee60915c4a6a3be5ae0c094f2`](https://github.com/aitishnyk/vacuum-voice-hub/commit/419ca0033874b11ee60915c4a6a3be5ae0c094f2)
passed the real owner-operated macOS
[GitHub Actions source-acceptance job #38089303529](https://github.com/aitishnyk/vacuum-voice-hub/actions/runs/38089303529):
full Python regression, model matrix, v2 integration/source audits, CLI,
Python and JavaScript syntax, public site build/verify, deterministic
SHA-256 release bundle, and macOS PyInstaller packaging all succeeded.

Earlier [v2 integration PR #66](https://github.com/aitishnyk/vacuum-voice-hub/pull/66)
passed 351/351 Python tests, CodeQL, Public Site, Release Bundle and
Windows/macOS/Linux package builds **on that PR head**. Such earlier
checks are not presented as exact-tag Windows/Linux or CodeQL acceptance.

**Release exception requested by owner:** GitHub-hosted main CI, CodeQL
and independent Windows/Linux desktop packaging were deferred after the
GitHub-hosted runner repeatedly failed before starting any steps. This
source release may be published manually from a Mac only with
`ops/release/publish-v200-source.sh`, which verifies the successful Mac
Actions SHA, refuses executable/source changes since it, builds/verifies
five public assets and checks the published bytes and tag SHA. It does
not falsely assert a green GitHub-hosted CI, vendor-approved hardware,
independent copyright clearance, or signed/notarized desktop packages.

The GitHub tag additionally provides GitHub's standard source archives.
The custom `VacuumVoiceHub-public-2.0.0.zip` contains the public static
catalog/site and metadata **not a signed desktop app**. `SHA256SUMS`,
`release-manifest.json`, `update-feed.json` and `sbom.spdx.json`
are provided for integrity and distribution metadata. This release
contains no user Creator backups, secret tokens or licensed voice files.

For a complete delivery/status matrix and deferred external validation,
see [v2 delivery closure](V2_DELIVERY_CLOSURE.md).
