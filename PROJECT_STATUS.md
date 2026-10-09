# Project status — v1.1.0 SOFTWARE STABLE / SOURCE SEALED

**Scope:** independently tested offline open-source software, not a guarantee
that all researched robot models accept custom voices. The existing
[v1.0.0 stable GitHub Release](https://github.com/aitishnyk/vacuum-voice-hub/releases/tag/v1.0.0)
remains immutable at `03e8457e024a05d6c256b4b4a71c2453ac287e72`.

## v1.1.0 exact acceptance

- Functional [PR #52](https://github.com/aitishnyk/vacuum-voice-hub/pull/52)
  exact feature head `d0e6c98fdea5539eb25fe3355a282b82ab813033`
  was merged into `main` at `111d5bd20229e2beef7ff8e1970d7a1a27867baa`.
- Feature head: **265/265 Python PASS**, CodeQL (Python+Actions) PASS,
  model matrix + software-stable audit PASS, Public Site PASS,
  Release Bundle PASS, and macOS/Windows/Linux Desktop Packages PASS.
- Independent merged-main [CI run #37978249472](https://github.com/aitishnyk/vacuum-voice-hub/actions/runs/37978249472):
  **265/265 PASS**, Model Matrix PASS, software-stable audit PASS, compile,
  CLI smoke and JS syntax PASS. Public Site and CodeQL checks on this SHA
  also succeeded.
- Published public source tag **v1.1.0 is still pending** until the
  version-specific release workflow succeeds; this page must not be
  interpreted as confirmation that GitHub Release assets already exist.

## Functional scope

- All existing **223 model profiles**, original model aliases,
  **55 credited voice variants**, and **22 text-only scripts** preserved.
- New `vvh research hardware-scaffold` makes a strictly local, bounded,
  SHA-256 metadata-only per-model/firmware draft with every hardware observation
  initially false. Source binaries, file paths, device credentials and
  proprietary firmware are not included in JSON.
- Existing Creator Studio, individual/batch audio previews, offline TTS,
  QA, review and Ed25519 provenance remain unchanged.
- Only Xiaomi X10 (`dreame.vacuum.r2209`) remains the physically verified
  VVH custom-install target. New or volunteered devices need manual
  firmware-by-firmware evidence and rollback checks; software release is not
  delayed when donations are unavailable.
- No Telegram/Stars/Bunny paid-media infrastructure in this public project.

**SOFTWARE STABLE / SOURCE SEALED** does not mean manufacturer endorsement,
native-speaker proof for the 22 script locales, bundled licensed audio, notarized
desktop binaries or hardware compatibility for 223 devices.

See [community test guide](docs/COMMUNITY_HARDWARE_TESTING.md),
[stable software policy](docs/STABLE_SOFTWARE_V100.md) and
[release notes](docs/RELEASE_NOTES_V110.md).
