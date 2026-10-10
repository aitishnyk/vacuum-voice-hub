# Project status — v2.0.0 SOFTWARE COMPLETE / official publication independent

**Universal Voice Studio** is an integrated offline Creator research/QA
product layer. The v2 source introduces a real unified CLI API and
session-guarded local Creator UI panel aggregating catalog model identity,
language script coverage, audio recordings and source SHA-256, mapped
semantic events/collisions, optional translation/reviewer attestations,
and offline adapter readiness.

Existing functional stages preserved: v1.2 language/audio QA, v1.3
pronunciation, v1.4 firmware evidence, v1.5 local timeline editor,
v1.6 community inbox, v1.7 offline adapter interchange, v1.8 voice
library and v1.9 backup/recovery. All former data and CLI namespaces
remain supported without destructive migration.

**This is not proof of universal hardware installation**. 223 model
profiles are researched identities; 55 credited voice variants are
historical assets and >=22 script locales are *text*, not automatically
recorded audio. Xiaomi X10 remains the only model with independently
accepted physical VVH custom-install testing. Licensing, volunteer
claims, manufacturer signatures and desktop code signing are not
automatically verified.

Source-release gates remain independent: full Python regression,
CI/model preservation, security/CodeQL, public bundle and site,
Windows/macOS/Linux desktop builds, merged-main CI and immutable
GitHub v2.0 publisher (never claimed before their success).
The public ZIP contains source/catalog metadata, not copyrighted
voices or private Creator backups.

See [Universal Studio](docs/UNIVERSAL_STUDIO_V200.md),
[migration guide](docs/MIGRATION_V200.md) and
[roadmap](https://github.com/aitishnyk/vacuum-voice-hub/issues/55).

## v2 delivery closure

The complete v2 **software** feature scope is implemented, with safety PRs
#67 and #68 merged. Real GitHub Actions [macOS acceptance #38089303529](https://github.com/aitishnyk/vacuum-voice-hub/actions/runs/38089303529)
was `completed/success` on exact source SHA
`419ca0033874b11ee60915c4a6a3be5ae0c094f2`, covering full Python,
model/locale preservation, universal studio acceptance, public site,
deterministic release archives and macOS executable packaging.

Because hosted runner dispatch repeatedly failed **before steps started**,
the owner explicitly deferred a further CI/CodeQL/Windows/Linux test cycle.
This is a **source-only release exception**, not a fabricated verification.
`ops/release/publish-v200-source.sh` must refuse executable/catalog
changes since the Mac-accepted SHA and must checksum/round-trip-verify the
five public assets. Publication remains independently verifiable from
GitHub Releases, not inferred from source commits or this status file.
Signed installers, rights clearance and additional physical device support
are outside the source-only v2 acceptance.

See [delivery closure](docs/V2_DELIVERY_CLOSURE.md).
