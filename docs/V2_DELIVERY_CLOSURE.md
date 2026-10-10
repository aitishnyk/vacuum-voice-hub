# Vacuum Voice Hub v2.0 — delivery closure and evidence

This document separates the finished **open-source software v2.0 scope**
from optional real-world validation and platform release infrastructure.
It is not a certification of 223 firmware installations.

## Feature delivery

| Workstream | Software delivered in source | Deliberate boundary |
| --- | --- | --- |
| v1.2 Audio/language review | SHA-bound translation review, A/B playback and local audio QA | Human listening and native-speaker approvals are not fabricated |
| v1.3 Multilingual voice engine | Opt-in local Piper/eSpeak, licensed user-supplied weights, pronunciation lexicons and translation overlays | 22+ locales are text scripts, not 22 completed recordings |
| v1.4 Model/firmware intelligence | 223 model identities, aliases and per-firmware research evidence | Research identity is not custom-voice installation permission |
| v1.5 Creator 2.0 | Offline visual timeline, preview, mastering, bounded Creator workspace QA/build | No proprietary firmware bypass or overwrite of source audio |
| v1.6 Community research | Offline metadata-only inbox, hardware reporting and consent-driven evidence flow | Reports are not auto-promoted to verified |
| v1.7 Adapter SDK | Versioned, validated offline interchange and model adaptation reports | No execution of third-party adapter code or unrestricted installation |
| v1.8 Voice Library | Offline hash-based credited voice search/index | No redistribution without independently established rights |
| v1.9 Recovery | New-destination backup/restore and archive SHA-256 verification | User audio remains private and local |
| v2.0 Universal Studio | Integrated model/locale/audio/adapter inspection, read-only local browser/CLI, release metadata and migration guide | Offline build-readiness is not real robot install proof |
| v2 security closure | Safe unique Creator upload staging, atomic replacement, localhost Host/Origin/session restrictions, HTML escaping | Does not imply an external web service or cloud sync |

Historical inventories are unchanged: **223** researched model identities,
**55** attributed voice variants, **at least 22** text-only script locales.
The only independently accepted physical VVH custom-voice installation
baseline remains **Xiaomi X10** (`dreame.vacuum.r2209`). Other devices can
still be investigated, previewed and built for offline analysis but cannot
be declared physically installable without real device/firmware evidence.

## Source evidence already completed

- v2 integration [PR #66](https://github.com/aitishnyk/vacuum-voice-hub/pull/66):
  351/351 Python tests and security/CodeQL, public site, release archive,
  Windows/macOS/Linux desktop builds on its exact **PR head**.
- v2 Creator safety [PR #67](https://github.com/aitishnyk/vacuum-voice-hub/pull/67)
  and [PR #68](https://github.com/aitishnyk/vacuum-voice-hub/pull/68)
  merged to main.
- Real, owner-operated [macOS GitHub Actions run #38089303529](https://github.com/aitishnyk/vacuum-voice-hub/actions/runs/38089303529):
  `completed/success` on exact main source
  `419ca0033874b11ee60915c4a6a3be5ae0c094f2`.
  Full Python regression, model matrix, source v2 audit, CLI/JS,
  public site, reproducible bundle/SHA-256 and macOS PyInstaller passed.
- Final manual source release procedure refuses any executable or catalog
  changes after that accepted main source. Only release-related Markdown,
  README, project status and the isolated owner release script can differ.

## Deferred external acceptance — deliberately NOT claimed

- GitHub-hosted merged-main ubuntu-latest CI remains blocked at job
  initialization (0 executed steps); other GitHub-hosted jobs have the
  same infrastructure condition. Owner requested publication without
  another testing cycle.
- Independent Windows/Linux desktop packaging and CodeQL on the final tag
  are not asserted. Earlier PR-head green jobs do not cover a newer tag.
- Apple signing/notarization and signed Windows distribution need actual
  code signing identities and acceptance outside this source-only release.
- Manufacturer/custom-firmware installation on additional models needs
  consent, rights checks, actual robot playback/reboot and safe stock rollback.
- Recorded multilingual audio and native translation review remain
  contributor-provided evidence; no text locale is automatically audio.

## Owner-authorized final publication

`ops/release/publish-v200-source.sh` is an explicit, owner-operated
**source-only exception path** while GitHub-hosted Actions cannot schedule
jobs. It verifies the successful Mac Actions SHA and unchanged functional
source, builds and checksum-verifies the existing public release assets,
publishes the immutable v2.0.0 tag/releases via `gh`, and downloads the
five assets to verify uploaded bytes. **It does not rerun unit tests.**

Do not silently disable the normal GitHub-hosted CI-dependent publisher.
Do not publish to PyPI without a separate package/distribution review.
Do not include private recordings, unlicensed voice packs, proprietary
firmware, robot credentials, or developer signing keys.

Once publication succeeds, verify the exact tag SHA and the GitHub Release
page. The release itself is the authoritative publication status; do not
equate this Markdown file with proof that publication has occurred.

## Longer-term community roadmap (not v2 source blockers)

Native-speaker recordings, donated-device testing, new vendor firmware
transports and notarized installers are additive projects contingent on
real inputs and evidence. They should not cause speculative claims in a
public release or postpone working offline software.
