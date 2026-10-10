# Vacuum Voice Hub v1.2.0 — Offline Language Review and Audio A/B

This public release packages versioned **source/catalog metadata** and retains
the v1.1.x community-first, conservative hardware verification policy.

## Added
- `vvh scripts review-init`, `review-audit`, `review-mark`: explicit,
  attributable local human translation review. SHA-256 source snapshot makes
  altered source scripts/overlays invalid. Each decision creates a new file.
- `vvh creator audio-compare`: read-only comparison of 2 local clips with
  SHA-256, peak/RMS dBFS, duration, clipping, silence and warnings.
- Focused positive/negative regression and CLI acceptance.
- PR #54 exact-head acceptance: **275 passed**, Model Matrix + stable audit,
  CodeQL (Python/Actions), Public Site, Release Bundle, 3 OS desktop package jobs.

## Strict limits
- 223 model profiles are researched identities, not 223 approved installers.
- 55 credited voice variants and >=22 **text** script locales preserved.
- Xiaomi X10 is still the only physically verified VVH custom-voice target.
- Human language attestation is a claim; native fluency and licensing are not
  independently verified. A/B is engineering QA, not listening or LUFS.
- No audio, manufacturer packages, firmware or credentials are bundled in the public metadata archive.
- Future waveform editing, LUFS/true peak, native-speaker reviews for every
  language, and v1.3-v2.0 roadmap items are not represented as implemented.
