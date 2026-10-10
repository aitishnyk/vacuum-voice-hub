# v1.2 — Offline Language Review & Audio A/B

This increment adds two practical, strictly local quality-control workflows.

## Attributed translation review

```bash
vvh scripts review-init --language uk --model dreame.vacuum.r2209 --output draft.json
vvh scripts review-audit draft.json
vvh scripts review-mark draft.json --semantic clean.start --status approved \
  --reviewer "Native-speaker volunteer" --language-attested --output approved.json
vvh scripts review-audit approved.json
```

With a contributor overlay, pass `--overlay translation.json` to **every**
command. The review carries an exact SHA-256 digest of every source phrase,
semantic, text source and event mapping. Changes to the translation overlay,
model mapping or script invalidate the review. Duplicate JSON keys and
unattributed approval claims are rejected. Every mark creates a **new** JSON
file; previous reviews are never overwritten. Approval is an explicit human
claim, **not** independent proof of native-speaker competence or rights. A
translation review never creates audio or grants device install permission.

## Read-only audio A/B

```bash
vvh creator audio-compare ./source.wav ./candidate.wav
```

Analyzes two bounded local WAV/compressed recordings with the existing audio
QA pipeline, reports source SHA-256s, peak/RMS dBFS, durations, clipped and
silent sample percentages, warning lists and B-minus-A numeric differences.
The two original recordings remain byte-identical. This is an engineering
check rather than a listening or licensing decision; LUFS/true-peak metrics
are **not** claimed by this release.

## Scope boundaries

* Prior 223 researched profiles, 55 credited variants and >=22 script-only
  locales are preserved; no device transport is changed.
* Only Xiaomi X10 is physically certified by VVH; users and volunteers must
  provide exact model+firmware testing to certify additional installs.
* Community-owned audio is never uploaded by these commands.
* No copyrighted bundled audio or unauthorized manufacturer operations are included.
