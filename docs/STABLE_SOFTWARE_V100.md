# v1.0.0 — Stable software release criteria and community evidence boundary

The v1.0 stable milestone means **the offline software core is source-tested,
reproducibly built and documented**. It does NOT claim that all 223 robot IDs
can accept custom voice installation or that all 55 attributed variants have
the legal right to be mirrored/republished. The 22 text-script locales are
starting templates, not a library of native-speaker verified recordings.

## Release acceptance (all required)

1. 223+ catalog model identities and aliases preserved; 55 credited voice
   variants and 22+ reference-language locales retained; packaged model JSON
   exactly mirrors catalog JSON.
2. No previously unsupported device or manufacturer-signed firmware is marked
   installed/verified by model-name resemblance, generated package format, an
   inferred protocol or an automated test. Xiaomi X10 remains the VVH-only
   hardware-verified baseline.
3. Automated `python scripts/stable_release_audit.py` and
   `python scripts/model_matrix_audit.py` pass; full `pytest -q` passes;
   `python -m compileall -q vacuum_voice_hub` and web JS syntax pass.
4. Public Site and Release Bundle verified; package contracts include all
   recording review/signature, individual mastering and batch mastering schemas.
5. GitHub Actions pull-request CodeQL for Python/actions plus all desktop
   package builds for **macOS, Windows and Linux** pass on the **same exact PR
   head**, followed by new merged-main CI/CodeQL verification.
6. No private robot token, Wi-Fi password, address, donor personal data, vendor
   firmware or unlicensed audio is committed to the project.

## Physical hardware evidence and community testing

Device-specific acceptance continues independently after software v1.0.
Community contributors can submit redacted exact model/firmware/region,
audible playback, reboot persistence and original voice rollback evidence
using [the hardware testing guide](COMMUNITY_HARDWARE_TESTING.md). Suppliers,
manufacturers, and users may volunteer loans or donations, subject to separate
private shipping arrangements and editorial independence. Physical devices
are welcome but **not mandatory** for a stable software release.

Unsupported-local and signed-only devices remain build/research-only. A
third-party translation requires language review, and any republished audio
requires an explicit redistribution license. A signed source manifest
attests to the integrity of bytes, not manufacturer certification or rights.

## No auto-promotion rule

No automated script, community issue or manufacturer contribution is allowed
to flip `device_tested` or `allow_default` solely because similar models or
packages work. A device compatibility policy change requires a separate
reviewed commit and real evidence. Explicit opt-in experimental transports
remain opt-in and do not become guarantees. Hardware failures, including
unreliable stock rollback, must be disclosed.

## What v1.0 can actually do

List, compare and preview source-attributed voice variants across researched
models; generate/edit Creator workspaces; synthesize text scripts using
user-supplied local engines; run audio quality inspections; individually
and batch-master recording previews; produce checked semantic packages;
review/safely import signed source and human QA evidence; build public catalogs
and offline artifacts; provide hardware-evidence workflows to volunteers.
Hardware installation support is never universal.

## Remaining roadmap

Native-speaker reviewed translation refinements, more true sound recordings,
per-model physical acceptance and independently sourced event mappings, richer
DAW-like production UI and more verified transport adapters remain continuing
v1.x work. Their absence cannot be hidden by the stable label.

## Acceptance evidence — sealed v1.0 source

- Feature PR: [#48](https://github.com/aitishnyk/vacuum-voice-hub/pull/48), exact feature SHA `e7c31a033ed13a0314cfaba8d8fe2c789fcf3e99`; 250 Python tests PASS, model matrix and stable audit PASS, Public Site, Release Bundle, CodeQL and 3 desktop platforms all PASS.
- Main merge SHA: `5406260ce3abb19b53fd9cb3213eef7f93ab4a8d`. Independent [CI run #37973030945](https://github.com/aitishnyk/vacuum-voice-hub/actions/runs/37973030945) SUCCESS, [Public Site run #37973031112](https://github.com/aitishnyk/vacuum-voice-hub/actions/runs/37973031112) SUCCESS, CodeQL Python+actions checks SUCCESS.
- No independent signed/notarized desktop binary, no official GitHub Release publication, and no newly verified robot models are claimed.

## v1.1.0 acceptance extension

The v1.1 community testkit has source assurance evidence in [PR #52](https://github.com/aitishnyk/vacuum-voice-hub/pull/52), exact functional head `d0e6c98fdea5539eb25fe3355a282b82ab813033`: 265/265 PASS, Model Matrix, stable audit, CodeQL, Public Site, Release Bundle and all three desktop CI packages PASS. Independent merged-main SHA `111d5bd20229e2beef7ff8e1970d7a1a27867baa` passed CI (run 37978249472), Public Site and CodeQL. This proves software acceptance, **not physical compatibility**. The exact GitHub Release tag/assets for v1.1 must be verified separately after publication.
