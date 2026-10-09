# v0.16 — Voice Production Studio & Human Review

This release provides an **offline recording production checklist**, source-audio SHA-256 fingerprints, a transparent human review status flow and an export suitable for asking a collaborator to check pronunciation. All information remains local unless the user explicitly shares the resulting files.

## 1. Generate real target-model recording assignments

```bash
vvh creator review init ./my-voice \
  --model dreame.vacuum.r2209 --language ru \
  --output ./review-r2209.json

# Optional local overlay with human-translated extras
vvh creator review init ./my-voice \
  --model viomi.vacuum.v60 --language uk \
  --overlay ./uk-overrides.json --output ./review-viomi-uk.json
```

The resulting `vvh.production-review.v1` JSON file includes **all** distinct semantics from the target's conservative known event profile (not just the 16 core localized text templates). Each task contains one or more exact numeric event IDs, the existing translation if one is available, and an explicitly labeled *English reference (not translated)* for missing phrases. A task also shows the *currently assigned* audio path, file size and SHA-256 if a recording is present.

New reviews are always written outside the Creator workspace and fail closed if the destination already exists.

## 2. Human recording and approval lifecycle

```bash
vvh creator review audit ./review-r2209.json

vvh creator review mark ./review-r2209.json \
  --semantic clean.start --status recorded
vvh creator review mark ./review-r2209.json \
  --semantic clean.start --status listened --reviewer "Human reviewer"
vvh creator review mark ./review-r2209.json \
  --semantic clean.start --status approved --reviewer "Human reviewer" \
  --language-attested --rights-attested
```

A semantic can advance only `draft → recorded → listened → approved`. Audio must be present before advancing beyond draft. Listening requires a *named reviewer*. Approval also requires **two separate affirmative human attestations**: reviewed speech language and permission to redistribute this recording. These are declarations made by a person; the program **does not independently establish** the truth of these declarations or confer rights.

The review manifest records timestamps for listening/approval and optional notes (maximum 500 characters). Human decisions are intentionally stored separately from `vvh.voicepack.v1`, preserving the original Creator manifest and audio files.

## 3. Detect stale approvals, refresh changed recordings safely

```bash
vvh creator review audit ./review-r2209.json
vvh creator review refresh ./review-r2209.json
```

An audit reopens the original local workspace, recomputes SHA-256 of audio and its `manifest.json`, compares the exact event-to-text assignments and refuses to consider earlier approval valid when file contents or mappings have drifted.

A refresh re-reads the model's current files: **unchanged** tasks retain earlier human review states; newly assigned, altered or deleted recordings and modified translations reset affected tasks to `draft`. When an overlay was originally used, pass the same `--overlay` to audit, refresh, mark and bundle operations. No sound data or robot preferences are modified during review.

Review JSON can be edited by local filesystem users. These human attestations are *not* cryptographically signed; SHA-256 only detects changes relative to the recorded source snapshot, not identity impersonation, malicious manual alterations to both the audio and JSON, or legal rights.

## 4. Export review material (audio **excluded** by default)

```bash
vvh creator review bundle ./review-r2209.json --output ./review-only.zip

# Only if you intend to share private recordings and have the relevant rights:
vvh creator review bundle ./review-r2209.json \
  --output ./review-with-recordings.zip --include-audio
```

The ZIP always includes `review.json` and `audit.json`; the absolute machine workspace path is omitted. When audio is explicitly included it also contains the current file(s), verified against their SHA-256 fingerprints and capped at 100 MiB total of input recording data. All audio files must stay within the workspace; no arbitrary-path exports or silent file replacement. If a bundle build fails, its own new ZIP is removed; original recordings are preserved. A successful ZIP never grants hardware custom-voice installation authority.

## 5. Creator Studio

The localhost Creator Studio now has a **Human Review & Recording Checklist** panel: select a project, target model and script locale, create a review, pick tasks, advance their status with reviewer identity and explicit attestations, refresh after new recordings, audit hashes, or export a local ZIP. Audio inclusion is unchecked by default. The local authenticated API uses randomly generated review IDs, not arbitrary filesystem paths.

## 6. Testing and preservation

```bash
python -m pytest -q
python scripts/model_matrix_audit.py
vvh creator review --help
vvh release build --output release
vvh release verify release
```

Frozen invariants: **215 model profiles and aliases**, **55 source-attributed audio variants**, **18 text script locales**, former 109/154 device identity fixtures and the **Xiaomi X10-only VVH hardware-install verification boundary**. Audio signal QA, reviewer declarations and locally generated TTS do not expand physical robot installation support. The manufacturer-signed restrictions on newer models stay in force.
