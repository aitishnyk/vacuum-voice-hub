# v1.9 — Creator Recovery and Backup

Create an independent, reproducible local backup of a Creator Studio voice
project, verify every audio SHA-256, compare it to current recordings, and
restore **into a new directory only**:

```bash
vvh creator backup ./my-voice --output ./my-voice-backup.zip
vvh creator backup-verify ./my-voice-backup.zip
vvh creator backup-compare ./my-voice-backup.zip --workspace ./my-voice
vvh creator backup-restore ./my-voice-backup.zip \
  --output-dir ./my-voice-restored
```

The archive contains the actual private Creator `manifest.json` and
**only the audio referenced by that manifest**, plus an index with every
file SHA-256 and the manifest digest. No unrelated workspace files,
robot credentials, OS keyring data or device network state are copied.
Archives are deterministic (fixed timestamps, stable member order and
uncompressed local content) and size-bounded to 256 clips, <=25 MiB per
clip and <=256 MiB total. Any mismatched, duplicate, traversing, symlinked
or otherwise unsafe entry is rejected.

Restore never overwrites a workspace: it creates a new exclusive folder,
validates source and audio checksums, then checks the restored Creator
manifest. On failure it removes only the newly created folder.
Backup/export operations do not modify the original project or install
anything on a robot.

**Privacy:** unlike public metadata-only release ZIPs, these Creator
recovery ZIPs intentionally contain your voice audio, declared author
metadata and potentially your source notes. Keep them private or use
your own encrypted storage. They are NOT encrypted or signed by VVH,
are NOT uploaded to remote services, and a valid backup does NOT prove
redistribution rights or hardware compatibility.
