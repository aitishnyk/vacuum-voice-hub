# v0.9 Offline Package Research Workflow

Vacuum Voice Hub can **inspect locally held research candidates** and compare their exact bytes with source-attributed research reports. It never connects to a robot, discovers undocumented vendor endpoints, executes vendor code or changes installation policy.

## Commands

```bash
# Preserve the original vvh research backlog listing:
vvh research

# Inspect an archive without extracting it or installing it:
vvh research inspect ./candidate.zip --model xiaomi.vacuum.d101

# Validate a community evidence report independently:
vvh research validate-evidence ./evidence.json --model xiaomi.vacuum.d101

# Bind a report to an actual local archive using SHA-256, exact size and format:
vvh research inspect ./candidate.zip \
  --model xiaomi.vacuum.d101 \
  --evidence ./evidence.json
```

Results use `vvh.research-assessment.v1` and are JSON on stdout. To save locally, redirect to a file (`> assessment.json`). The report contains the archive digest, model and declared install policy, optional vetted evidence, per-entry inventory and strictly heuristic filename-pattern findings.

For packaged ZIP and TAR-family formats, inventory processing is bounded and **never extracts** archive members to disk. An opaque `.pkg` that is not recognizable as an archive may be hashed and recorded **without attempting decryption**. Deliberately malformed ZIP/TAR content renamed `.pkg` remains rejected. Unicode/non-portable member names, dangerous paths, case-collisions, links and special files are rejected by the inspector. Constraints are documented in [Archive Inspector](ARCHIVE_INSPECTOR_V09.md).

Recognized **research-only** patterns: numeric OGG names, `sound_*.mp3` IJAI-style names and selected Roborock WAV prompt names. Matching does not prove that any candidate was issued by the vendor, that arbitrary audio is authorized, or that a robot accepts the package. Non-matching and unknown numeric IDs are reported; **they are never pushed to a device**.

A matching evidence report requires exact canonical model ID, source HTTPS reference, archive SHA-256, byte size and compatible declared format. The offline tool does not fetch the source URL, verify authorship or certify a real hardware test; an alleged successful device report remains `hardware-review-required`.

## Model scope and reliability

The v0.9 research workflow applies to all existing **109** declared model profiles, including build-only Xiaomi H40, X20+, Mijia 5/6, Viomi and ROIDMI, and documented Dreame, IJAI and classic Roborock profiles. **It does not introduce or certify a new vendor adapter or transport**. Only Xiaomi X10 retains existing VVH physical hardware evidence. Build-only and signed-only models remain blocked for arbitrary custom installation.

## Quality gates

```bash
python -m pytest -q
python scripts/model_matrix_audit.py
python -m compileall -q vacuum_voice_hub
vvh stats
vvh research --help
vvh research inspect --help
vvh release build --output release
vvh release verify release
```

A production release must additionally pass the existing CI, desktop build, catalog and release-bundle workflows. Hardware certification requires independent exact-device test evidence beyond these software gates.

## Remaining hardware research for v1.0

Collect lawfully obtained, source-attributed sample packages and on-device acceptance reports for ROIDMI EVA/EVE, Xiaomi H40/X20+, Mijia 5/6, Viomi Alpha/V3 and modern Dreame. Until exact package formats and transport behavior are established, those targets remain research/build-only rather than presumed installable.
