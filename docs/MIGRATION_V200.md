# v1.x → v2.0 — Safe Source Migration

The move to `2.0.0` keeps the existing underlying data formats and
command namespaces. There is **no automatic data migration** and no
destructive project rewrite.

- Existing `vvh creator` projects retain `vvh.voicepack.v1` manifests.
- Existing `vvh scripts` overlays and pronunciation dictionaries remain
  opt-in and unchanged.
- Existing evidence reports, per-firmware checks and locally moderated
  snapshots are still research-only.
- Existing local adapter interchange ZIP, voice-library index and
  Creator backup archives remain their documented v1 schemas.
- New `vvh studio inspect` and `vvh studio report` only read existing
  artifacts. Reports are exclusively created at new paths.
- Never infer new physical install support from catalogue presence.
  Existing supported transports are unchanged.

Before upgrading: back up your Creator projects locally with the v1.9
`vvh creator backup` workflow, verify ZIP integrity, and keep those
backups private. Public source ZIPs **do not** contain private audio.
Any installed signed desktop application must be updated according
to its OS signing trust boundary; the public metadata-only release
does not claim a newly signed/notarized desktop installer.

Hardware verified within VVH remains Xiaomi X10 only until
model+firmware-specific real tests are independently accepted.
All 223 previously researched model IDs and aliases, 55 credited
voice variants, and >=22 text-only locales are preserved by
machine-executable software release audits.
