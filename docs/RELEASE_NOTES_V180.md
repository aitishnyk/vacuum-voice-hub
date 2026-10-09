# v1.8.0 — Offline Attributed Voice Library

A genuinely usable local metadata index is available through
`vvh library index/search/audit/reconcile`. It checks real Creator
workspace manifests and actual audio hashes, safely omits local paths,
source recordings and sensitive network details, and detects changed
source audio after indexing.

- Stable `vvh.local-voice-library.v1` JSON, exact source fingerprints.
- Search by title/author/id, language and declared license.
- Bounded indexing and fail-closed duplicate/symlink/invalid input.
- Original Creator recordings are not modified, copied or uploaded.

**A license string is a contributor claim, not independent legal
verification.** No voice is automatically labeled verified or
redistributable, and no new device install permission is granted.

Historical baseline retained: 223 researched model profiles,
55 attributed prerecorded variants, >=22 text-only language templates,
Xiaomi X10 as VVH's only physically verified custom-install target.
Public release artifacts remain metadata/catalog, not copyrighted
audio collections or signed desktop installers.
