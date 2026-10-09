# v1.4 — Model & Firmware Evidence Matrix

This local research feature combines **untrusted self-reported hardware tests**
for an exact canonical robot model without contacting the robot or changing
its install policy.

```bash
vvh research firmware-matrix --model dreame.vacuum.r2209 \
  --report ./volunteer-a.json --report ./volunteer-b.json
```

The input reports use the existing `vvh.hardware-acceptance.v1` schema.
Each one must include the candidate package digest and all five explicit
observations (signature review, download, playback, reboot, stock rollback).
This matrix validates exact model/firmware, safe JSON and source hashes,
highlights differing packages and claims for a firmware, and reports
**ready for independent review** rather than pretending testing has
been accepted. A completely checked volunteer report is still NOT a
hardware verification by the maintainers.

Output intentionally omits source file paths, URLs and candidate bytes.
Symlinks, malformed/oversized/duplicate JSON, secret-containing reports,
wrong-device claims and duplicate report hashes are rejected.
Only Xiaomi X10 was already hardware-tested in the historical registry;
this command never changes that status or authorizes new firmware or
voice package installers.
