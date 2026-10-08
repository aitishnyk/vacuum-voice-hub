# Distribution Hardening

Vacuum Voice Hub v0.7 adds a deterministic release-bundle contract.

## Build

```bash
export SOURCE_DATE_EPOCH=1700000000
vvh release build --output release
vvh release verify release
```

Output:

```text
release/
├── VacuumVoiceHub-public-0.7.0.zip
├── sbom.spdx.json
├── release-manifest.json
├── update-feed.json
└── SHA256SUMS
```

## Contracts

- `vvh.release-manifest.v1` — artifacts, digests, distribution contracts, desktop build names and signature state.
- `vvh.update-feed.v1` — stable-channel pointer to the current release manifest/public bundle.
- `SHA256SUMS` — external digest list for release files.
- `sbom.spdx.json` — SPDX 2.3 package SBOM with direct runtime requirement metadata.

## Reproducibility

The release builder:
- uses `SOURCE_DATE_EPOCH`;
- gives ZIP members deterministic timestamps and permissions;
- sorts JSON keys;
- omits random IDs and wall-clock timestamps;
- rebuilds the public catalog from canonical data.

The CI Release Bundle gate builds twice with the same git-derived epoch and requires `diff -qr` to report no differences.

## Desktop artifacts

Desktop binaries are produced by the separate three-OS `Desktop Packages` workflow.

The source release manifest lists the expected desktop artifact names but deliberately sets:

```json
"hashes_in_this_manifest": false
```

until a trusted release orchestration job collects those exact binaries and writes their hashes. This prevents pretending a binary checksum is known when it is not.

## Verification

```bash
vvh release verify release
```

Verification checks:
- artifact existence;
- byte size;
- SHA-256;
- update-feed → release-manifest digest link;
- `SHA256SUMS`.

## Signing boundary

Source/PR builds are intentionally unsigned. See [SIGNING.md](SIGNING.md).
