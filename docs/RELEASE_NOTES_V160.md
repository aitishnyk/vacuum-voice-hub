# v1.6.0 — Offline Community Evidence Moderation

v1.6.0 adds a functional metadata-only community research queue using
local `vvh community init/add/moderate/audit` commands.

- New-only immutable snapshot workflow; exact report SHA-256 binding,
  canonical model identity and firmware, no raw volunteer reports retained.
- Strict safe evidence validation, duplicate and symlink rejection, bounded
  256 submissions/reviews, redacted metadata and no secrets/URLs in output.
- Explicit human research decisions and hash-linked local audit history.
  Checksums detect inconsistency, but are NOT signatures.
- Independent acceptance never inferred from volunteer reports; no device
  controls, voice audio uploads, vendor firmware or private information.
- Historical 223 model profiles, 55 attributed voice variants, >=22
  text-only locales and Xiaomi X10-only VVH physical install confirmation
  retained.

This ZIP is public source/catalog metadata, **not a signed executable**,
manufacturer-endorsed device adapter, licensed audio collection or an
online community hosting service.
