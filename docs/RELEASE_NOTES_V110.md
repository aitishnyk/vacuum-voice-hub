# Vacuum Voice Hub v1.1.0 — Community Hardware Test Kit

v1.1.0 is the next stable **offline software** release after v1.0.0.
It does not change which physical vacuums are known to accept custom voice packages.

## New in v1.1

Create a **metadata-only** device test checklist using a local candidate:

    vvh research hardware-scaffold --model roborock.vacuum.a75 \
      --firmware 1.2.3 --package ./candidate.pkg --output ./device-evidence.json
    vvh research hardware-acceptance ./device-evidence.json --model roborock.vacuum.a75

The command hashes a local candidate in bounded streaming chunks, checks exact
canonical model identity and a non-sensitive firmware version, and refuses
symlinked, empty or oversized packages or overwriting existing reports.
The new JSON has SHA-256 and byte size, **not the package, private file paths or
robot credentials**. All five hardware observations default to **false** until
a volunteer actually tests the unit and supplies redacted public HTTPS evidence.
Self-reported success does not authorize an installer or change compatibility.

## Preserved v1.0 capabilities

- 223 researched robot models and legacy aliases; 55 attributed voice variants;
  22 **text-only** reference languages.
- Creator Studio, scripts, optional local synthetic voice generation,
  individual and batch offline audio mastering, SHA-256 QA and Ed25519 review
  provenance.
- Public catalog and release artifacts with a CI-enforced software baseline audit.

Only Xiaomi X10 (dreame.vacuum.r2209) remains VVH physically verified for custom
voice installation. Other devices require exact firmware-level evidence and
independent evaluation. Community reports and voluntary manufacturer/user
loans or donations are welcome but confer no favorable verdict or support
deadline.

## Published assets

Assets include the public catalog ZIP, release manifest, update feed, SHA256SUMS
and SPDX SBOM, plus GitHub source archives. No copyrighted third-party recordings,
proprietary firmware or robot credentials are distributed. Mac, Windows and
Linux desktop builds are tested by CI, not distributed here as signed or
notarized installers.

See docs/COMMUNITY_HARDWARE_TESTING.md and docs/STABLE_SOFTWARE_V100.md.
