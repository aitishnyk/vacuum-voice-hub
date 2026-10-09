# v0.17.0 — Returned Reviewer Handoff & Firmware Evidence

This release extends the **local** Voice Production Studio. It treats reviewer decisions and reported hardware observations as research assertions — not independent proof of the reviewer’s identity, redistribution rights, native pronunciation, or manufacturer permission to install voice packs.

## Import a returned review safely

Export a review checklist in v0.16:

```bash
vvh creator review bundle ./review.json --output ./review-to-send.zip
```

The default ZIP contains **review.json** and **audit.json**, without audio. A collaborator may inspect and edit the returned `review.json` to record their listening notes and reviewer decisions, or return a reviewed ZIP containing it.

Explicitly bind the returned material to your existing local Creator workspace:

```bash
vvh creator review import ./returned-review.zip \
  --workspace ./my-voice --model dreame.vacuum.r2209 --language ru \
  --output ./returned-claims.json
vvh creator review audit ./returned-claims.json
vvh creator review history ./returned-claims.json
```

The importer checks model ID, locale, pack ID, *exact source manifest SHA-256*, text/event-ID mapping and the current SHA-256 of every local assigned audio file. When a ZIP contains optional audio, hashes of all included samples must match the already-existing local workspace recordings. Files are **never extracted to disk**, and no original Creator audio is overwritten. Unsafe paths, duplicate entries, symlinks, encrypted ZIP content, malformed/oversized documents and unexpected member names are rejected.

**Critical trust boundary:** the remote `Approved` status is stored only as an `external_review_claim` with `trusted=false`. The new *local* review starts with every task at `draft`; no imported approval, license permission or robot install authorization is transferred. A local reviewer must follow the ordinary `recorded → listened → approved` process again.

For browser import, select a returned **metadata-only** JSON or ZIP of up to 2 MiB in Creator Studio's Human Review panel. For larger ZIPs with explicitly included audio, use the CLI, which enforces per-entry and total uncompressed-size bounds.

## Inspect local review history

```bash
vvh creator review history ./returned-claims.json
```

When a local reviewer changes a status, or refreshes changed recording assignments, the application writes a timestamped, SHA-256-linked event to a sibling `*.history.jsonl` file. An import adds an `import-return` event. Auditing rejects an inconsistent hash chain or a current review file changed outside the journal.

This is **tamper-evident under ordinary file changes**, not digitally signed. A malicious party with write access to both the source and history can rewrite the chain, and the timestamps/reviewer names are local claims. Cryptographic identity verification and provider-backed evidence are separate future work.

## Hardware + firmware acceptance intake

```bash
vvh research hardware-acceptance ./hardware-report.json \
  --model roborock.vacuum.a75
```

A bounded local `vvh.hardware-acceptance.v1` JSON report requires an **exact canonical model ID**, firmware version, candidate package SHA-256 and size, and five explicit yes/no observations: signature review, device download, audible playback, reboot persistence, and stock rollback verification. Every positive observation needs a reference URL.

The tool returns either `incomplete-research-only` or `ready-for-independent-hardware-review`. **Neither** status changes installer policy: `install_authorized=false`, `registry_mutated=false` and `transport_policy_changed=false`. Even five asserted successes are not independently authenticated or evidence of manufacturer signing compatibility.

## Regression and preservation

```bash
python -m pytest -q
python scripts/model_matrix_audit.py
vvh creator review import --help
vvh creator review history --help
vvh research hardware-acceptance --help
vvh release build --output release
vvh release verify release
```

All previous **215 models** and aliases, **55 attributed voice variants**, **18 text-only script locales**, both frozen 109/154 identity test fixtures, and the Xiaomi X10-only VVH physical verification boundary must remain unchanged. Any future custom-voice transport needs independent exact-device+firmware testing, safety rollback acceptance and separately authorized implementation.
