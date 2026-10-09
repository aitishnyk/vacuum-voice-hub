# Project status — v1.4.0 SOFTWARE STABLE (source)

v1.4.0 introduces a read-only, exact-model and per-firmware evidence matrix
for community-supplied `vvh.hardware-acceptance.v1` reports. Individual
self-reports are validated but NEVER automatically accepted as physical
installation support; no firmware, robot, transport, audio library, public
source catalog or registry is mutated.

The feature is independently CI-tested in its GitHub PR, with main CI,
CodeQL, three desktop builds, software preservation audit and GitHub
Release publication as separate mandatory gates.

**Preservation:** >=223 source-attributed model identities; 55 credited
voice variants; >=22 script-only locales. **Only Xiaomi X10**
(`dreame.vacuum.r2209`) was physically verified for VVH custom install.
No automatically approved community devices.

See [v1.4 documentation](docs/FIRMWARE_MATRIX_V140.md)
and [roadmap tracker](https://github.com/aitishnyk/vacuum-voice-hub/issues/55).
