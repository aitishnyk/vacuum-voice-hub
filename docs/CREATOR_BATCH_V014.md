# v0.14 — Multi-Model Creator Preflight & Batch Builds

v0.14 improves **offline voice adaptation** across the preserved 215 canonical robot profiles. It does not add any newly verified device transport, unlock region restrictions, remove manufacturer signatures, or download community audio.

## 1. Inspect whether audio is usable for a particular model

```bash
vvh creator preflight /path/to/creator-project --model dreame.vacuum.r2209
vvh creator preflight /path/to/creator-project --model viomi.vacuum.v60 --check-audio
```

The `vvh.creator-preflight.v1` JSON report includes:
- exact model identity, adapter, package/container suffix and model event profile;
- mapped numeric IDs, all missing IDs, missing core IDs with semantic keys and descriptions;
- unmapped source semantics, case-safe per-input relative paths, exact size and SHA-256 fingerprints;
- conflicting mappings: more than one semantic assigned to the **same numeric ID**;
- optional bounded **16-bit PCM WAV signal QA** warning indicators (silence, clipping, excessive duration).

A preflight is marked `ready` only if 5+ mapped events remain, the mappings are non-ambiguous and no WAV is structurally invalid when checked. A `ready` result **never** means the robot accepts that vendor voice format. Unrecorded core events remain explicit warnings rather than being fabricated or silently replaced.

## 2. Build one workspace into multiple independent artifacts

```bash
vvh creator batch /path/to/creator-project \
  --model dreame.vacuum.r2209 \
  --model xiaomi.vacuum.d101 \
  --model roborock.vacuum.a75 \
  --output-dir /path/to/new-build-directory \
  --check-audio
```

The process:
- Canonicalizes each model ID and rejects duplicates.
- Restricts batch size to **1–16** targets and refuses pre-existing output directories.
- Rejects ambiguous event mappings, unsafe/unavailable audio and too-small event coverage before generating anything.
- Builds a separate package with the existing adapter for **each model**. For unverified Xiaomi/Viomi/Roborock/ROIDMI/IJAI, this means a portable research-only semantic ZIP; it is **not** a manufacturer-installable pack.
- Stores SHA-256 for every resulting file and output model list in `manifest.json` (`vvh.creator-batch.v1`).
- Detects source-audio changes that occur during the build and deletes its own unfinished new batch directory on failure; existing projects and output directories are not overwritten.
- Requires **separate human licensing and physical-device verification** for any future distribution or installation.

The 215 model profiles and original 55 source-attributed voice variants remain untouched. The available software matrix is still **11,825 model × voice** targets, not 11,825 verified installations. The 18 localized text-script templates and local Piper/eSpeak engines remain separate Creator workflows.

## 3. Creator Studio (localhost Web UI)

Run `vvh web` and visit `/creator`:
- Choose an existing workspace and a target model; click **Preflight** to display mapping, missing core prompts, collisions and WAV warnings.
- For an offline batch, enter comma-separated exact model IDs in the new **Build batch** panel and optionally enable WAV QA.
- Local API `GET /api/creator/preflight?id=<workspace-id>&model_id=<id>&check_audio=true` returns the read-only plan; authenticated `POST /api/creator/batch` accepts `{"id":"workspace-id","models":["id1","id2"],"check_audio":true}`.
- The API writes a new unique output directory under the local platform data directory `creator-batches/`. It does not accept arbitrary output paths from the Web UI or access the robot.

## 4. QA and release

```bash
python -m pytest -q
python scripts/model_matrix_audit.py
python -m compileall -q vacuum_voice_hub
vvh creator preflight --help
vvh creator batch --help
vvh release build --output release
vvh release verify release
```

Required preservation: 215 prior model IDs and aliases, all 55 source-linked voice identities, 18 text locale templates, inherited 109/154-model identity baselines, and the **Xiaomi X10-only physical installation verification**. No new custom-install capability is inferred from this software release.
