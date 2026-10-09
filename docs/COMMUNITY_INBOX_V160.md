# v1.6 — Offline Community Research Review Inbox

The open-source application includes a fully local, copy-on-write,
metadata-only moderation workflow for volunteer hardware reports. It does
**not** host a submission website, receive remote uploads, solicit shipping
addresses, or run hardware installation commands.

```bash
vvh community init --output ./inbox-001.json
vvh community add ./inbox-001.json --report ./volunteer-x10.json \
  --output ./inbox-002.json
vvh community audit ./inbox-002.json
vvh community moderate ./inbox-002.json \
  --submission <64-character report SHA256> \
  --decision needs-evidence --reviewer "Community maintainer" \
  --note "Independent stock rollback evidence is missing" \
  --output ./inbox-003.json
```

Every output is an exclusively created **new JSON file**; the previous
snapshot is never modified. The inbox stores only the report SHA-256,
canonical model ID, sanitized firmware string, package SHA-256, claimed
test stages and attributable moderation history. It deliberately excludes
evidence URLs, local paths, source metadata, firmware/audio bytes, IPs,
device tokens and other sensitive input. Contributions must use
`vvh.hardware-acceptance.v1`; malformed, secret-containing, duplicated,
oversized and symlinked reports fail closed.

Each snapshot includes a SHA-256 self-checksum and a reference to the
previous snapshot; moderation decisions contain a hash-linked history.
These are **local integrity checks, not digital signatures** and cannot
prove independence or authenticity. A reviewer can mark a submission
`research-accepted`, `needs-evidence`, or `rejected`; none of these
statuses approves hardware/firmware or enables an installer.

Anyone offering to lend a device should communicate directly with the
maintainers outside the inbox. Do not put names, shipping addresses,
serial numbers or passwords into the reports. Device acceptance still
requires independent model+firmware tests, playback and stock rollback.
Only Xiaomi X10 has prior verified VVH custom-install evidence.
