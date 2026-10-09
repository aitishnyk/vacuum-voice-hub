# Vacuum Voice Hub

[![CI](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/aitishnyk/vacuum-voice-hub/actions/workflows/ci.yml)

**Credits-first multi-model voice platform for robot vacuums.**

## v0.18.0 — Signed Reviewer Provenance & QA Evidence

Offline, **optional Ed25519** reviewer attestation binds a current approved Creator recording SHA-256, target model, locale, event IDs, translated-text digest and specific reviewer claim to a detached JSON signature. The private PEM key is supplied **only from your local filesystem**; never auto-generated, uploaded or persisted by VVH. Verification requires a separately supplied public key and rechecks the *current* recording and review. A valid signature proves possession of a key, **not** legal ownership, native pronunciation or robot installation support.

```bash
vvh creator review attest ./review.json --semantic clean.start \\
  --private-key ./my-ed25519-private.pem --output ./signed-review.json
vvh creator review verify-attestation ./signed-review.json \\
  --public-key ./reviewer-public.pem --review ./review.json
vvh creator review audio-acceptance ./review.json --max-clips 16
```

Install the optional CLI key handler with `pip install 'vacuum-voice-hub[review-signing]'`. Packaged desktop builds include its optional cryptography dependency. A Creator Studio panel also separates human review status from WAV/opt-in compressed audio signal QA and offers **non-authorizing** model/firmware/playback/reboot/stock-rollback evidence checks. [Full v0.18 guide](docs/REVIEWER_PROVENANCE_V018.md).

## v0.17.0 — Reviewer Handoff Import & Hardware Evidence

Import a collaborator's returned **JSON or ZIP** review against the *exact local model, source pack, translated script and original audio SHA-256 hashes*. No ZIP entries are extracted and no existing audio is overwritten. Returned approvals are stored as **untrusted external claims**; every local review starts at `draft` and must be independently approved again. A local hash-linked `review history` records later decisions (not a digital signature).

```bash
vvh creator review import ./returned-review.zip --workspace ./my-voice \\
  --model dreame.vacuum.r2209 --language ru --output ./returned-claims.json
vvh creator review history ./returned-claims.json
vvh research hardware-acceptance ./evidence.json --model roborock.vacuum.a75
```

Creator Studio accepts small metadata-only handoffs (up to 2 MiB). The new hardware evidence format tracks exact firmware, package fingerprint, claimed playback/reboot and stock rollback but **never** unlocks custom install transports. See [v0.17 secure handoff guide](docs/REVIEW_HANDOFF_V017.md).

## v0.16.0 — Voice Production Studio & Human Review

Creator Studio now includes offline **per-model recording assignments** for every known semantic event, a saved human review workflow (`draft → recorded → listened → approved`), source-file **SHA-256 integrity checks**, and an explicit **review bundle** export. Changes to recordings or the Creator manifest invalidate old approvals; a `refresh` preserves unchanged review decisions and resets only changed tasks.

```bash
vvh creator review init ./my-voice --language ru --model dreame.vacuum.r2209 --output ./review.json
vvh creator review audit ./review.json
vvh creator review mark ./review.json --semantic clean.start --status recorded
vvh creator review mark ./review.json --semantic clean.start --status listened --reviewer "Editor"
vvh creator review mark ./review.json --semantic clean.start --status approved --reviewer "Editor" --language-attested --rights-attested
vvh creator review bundle ./review.json --output ./reviewer.zip
```

Review ZIPs contain **metadata only by default**. Include private audio recordings only with `--include-audio`; no network upload or automatic robot installation occurs. The statements about spoken language and distribution rights are *human attestations*, not independently verified legal grants or certification. See [v0.16 production review guide](docs/VOICE_PRODUCTION_REVIEW_V016.md).

## v0.15.0 — Real Compressed Audio QA & Language Coverage

Optional **offline FFmpeg** inspection of MP3, OGG, FLAC, M4A, AAC and Opus, in addition to WAV; a gain-only WAV **preview** that never alters the source; and a report separating actual Creator audio assignments from the text translated for each of 18 locales. Existing model/voice inventories and installation restrictions are unchanged.

```bash
vvh creator qa /path/to/workspace --model dreame.vacuum.r2209 --decode-compressed
vvh creator preflight /path/to/workspace --model viomi.vacuum.v60 --check-audio --decode-compressed
vvh creator gain-preview ./voice.mp3 --gain-db -5 --output ./voice-preview.wav
vvh creator language-coverage /path/to/workspace --language uk --model dreame.vacuum.r2209
```

Decoder outputs are bounded to a local temporary PCM file (no network, no third-party upload), and analysis stays opt-in. See [Compressed Audio QA v0.15](docs/COMPRESSED_AUDIO_QA_V015.md). Matching a voice's declared locale does not verify what language is spoken, audio rights or actual firmware custom-voice compatibility.

## v0.14.0 — Multi-Model Creator Build & Adaptation QA

Creator Studio can now **preflight** audio for a particular model, show missing core prompts and conflicts, and build one approved workspace into independent offline voice packages for up to **16 target models** at once. Each file receives SHA-256 integrity metadata; source changes during the build or any target failure abort the batch without overwriting user files.

```bash
vvh creator preflight /path/to/workspace --model viomi.vacuum.v60 --check-audio
vvh creator batch /path/to/workspace \\
  --model dreame.vacuum.r2209 \\
  --model viomi.vacuum.v60 \\
  --output-dir /path/to/new-batch --check-audio
```

The localhost Creator Studio adds Preflight and Build batch controls. Output is for offline review/build only; **no robot installation is triggered or certified**, and licensing/safety require human review. See [v0.14 Creator Batch guide](docs/CREATOR_BATCH_V014.md).

## v0.13.0 — Multi-Brand Robot Discovery

**215 source-attributed device profiles** across Xiaomi/Mijia, Viomi, Roborock, ROIDMI, IJAI and existing Dreame/MOVA families. New in v0.13: 61 identity-verified **portable research-only profiles** and a local model-event comparison tool. The existing **55 original voice variants**, **18 text-script locales**, legacy IDs and installation policies are preserved.

**11,825 model × voice software combinations** are available for coverage and preview. This number must not be interpreted as verified installed voices on 215 physical robots. All newly imported models are `semantic_bundle`, `unsupported-local`, `build-only` and lack any bypass or direct voice upload.

```bash
vvh models --vendor Roborock
vvh models --search "Viomi"
vvh model-compare xiaomi.vacuum.d101 xiaomi.vacuum.ov51gl
vvh model-compare roborock.vacuum.a73 viomi.vacuum.v60
```

Source traceability and the exact new-model matrix: [v0.13 Multibrand Discovery](docs/MULTIBRAND_DISCOVERY_V013.md). An exact model identity or common voice events do not prove manufacturer package signing or installation support.

## v0.12.0 — Extended Language Pack Translation Studio

**New:** local author-attributed translation overlays can add further semantic events to the 16 built-in phrases, for any existing model profile, and can be used with **both** eSpeak-NG and Piper synthesis. These extra translations are user-supplied text, not new prerecorded voices or new verified device installs.

```bash
# Generate untranslated English-reference candidates for your specific model:
vvh scripts scaffold --language uk --model dreame.vacuum.r2209 --output ./uk-scaffold.json

# Fill a separate vvh.translation-overlay.v1 file with reviewed translated strings.
vvh scripts audit --language uk --model dreame.vacuum.r2209 --overlay ./my-uk-overrides.json
vvh scripts show --language uk --model dreame.vacuum.r2209 --overlay ./my-uk-overrides.json
vvh scripts piper --language uk --model dreame.vacuum.r2209 \\
  --id my-uk-full-pack --author "Local creator" \\
  --voice-model /path/to/uk_UA-voice.onnx \\
  --overlay ./my-uk-overrides.json --allow-synthetic
```

Overlays are bounded, must declare locale/author/license, reject unknown catalog semantic keys, and never authorize installation. See [translation overlay guide](docs/TRANSLATION_OVERLAYS_V012.md).

## v0.11.0 — Offline Piper & Audio Quality Studio

**New:** opt-in Piper TTS with existing local `.onnx` + `.onnx.json` files (no model downloads), read-only WAV signal analysis, whole Creator workspace QA and a local Creator Studio Audio QA button. Source v0.11.0 retains all 154 models, 55 attributed voice variants and 18 script locales. No newly verified custom installation routes.

### Neural TTS with a local licensed Piper voice

```bash
vvh scripts piper --language ru --model dreame.vacuum.r2209 \\
  --id my-ru-piper --author "Local creator" \\
  --voice-model /path/to/ru_RU-voice.onnx --allow-synthetic
vvh creator qa /path/to/creator/workspace --model dreame.vacuum.r2209
```

The Piper voice model and its matching `.onnx.json` config must already exist on disk; the config language must match the chosen script locale. The generated WAVs are local, may need correction by a native speaker and remain **UNLICENSED** pending explicit license review. Signal QA reports loudness, clipping, duration and silence heuristics; it does not claim intelligibility or device compatibility.

## v0.10.0 — Expanded Model & Language Studio

The v0.9.1 security update replaces legacy archive extraction with bounded, symlink-safe ZIP/TAR streaming on Python 3.10+; unsafe archive names, special members, collisions and excessive sizes fail closed.


Vacuum Voice Hub v0.10 provides **154 model profiles** and retains **55 source-attributed recorded voice variants** — an **8,470 software model × voice target** matrix. It additionally provides **18 text-only script locales** (16 common event prompts each) and optional local espeak-ng WAV synthesis into Creator Studio.

Target families:

- **51 Dreame numeric** targets;
- **33 Roborock** targets;
- **8 IJAI** targets;
- **62 portable semantic/build-only** targets.

All targets participate in model-aware compatibility, preview and Creator Studio. Installation remains evidence-scoped: Xiaomi X10 is the only VVH hardware-verified device; experimental or vendor-signed limitations are shown explicitly.

Read [v0.10 Expansion & Language Studio](docs/MODEL_LANGUAGE_EXPANSION_V010.md), [Mass Model Expansion](docs/MASS_MODEL_EXPANSION.md), the full [Model Matrix](docs/MODEL_MATRIX.md), and the [v0.9 Offline Research Workflow](docs/RESEARCH_WORKFLOW_V09.md).

### New in v0.9 — offline package research

- safe bounded archive inventory for ZIP/TAR without extracting or running untrusted files;
- SHA-256 + size validation of exact candidate against optional vvh.transport-evidence.v1 reports;
- conservative numeric OGG, IJAI MP3 and Roborock WAV filename-pattern discovery;
- cross-check against the chosen model's declared event profile;
- versioned research schemas, CLI and negative regression tests;
- opaque proprietary .pkg metadata intake without decryption or installation.

```bash
vvh research inspect ./candidate.zip --model xiaomi.vacuum.d101
vvh research validate-evidence ./evidence.json --model xiaomi.vacuum.d101
vvh research inspect ./candidate.zip --model xiaomi.vacuum.d101 --evidence ./evidence.json
```

**v0.9 does not certify new custom-install transports.** Filename similarities and community reports do not constitute robot hardware tests. Build-only/official-signed-only restrictions remain in force.

## New commands in v0.10

```bash
vvh models --search "Dreame"
vvh models --adapter semantic_bundle
vvh models --hardware-verified
vvh languages
vvh scripts list
vvh scripts show --language ru --model xiaomi.vacuum.d101
vvh scripts export --language uk --model dreame.vacuum.r2209 --output ./uk-script.json
```

**Optional local synthetic audio** (no cloud TTS; requires `espeak-ng` installed):

```bash
vvh scripts synth --language ru --model dreame.vacuum.r2209 \
  --id custom-russian --author "Local author" --voice ru --allow-synthetic
```

This produces a private Creator workspace with generated WAV files; it does **not** automatically install audio on any robot. Text-only scripts are not counted as available prerecorded voice packs, and the quality/redistribution rights of local TTS must be reviewed.

## Main capabilities

- 55 source-attributed community voice variants;
- Russian, Ukrainian, English and additional language packs;
- 18+ packs hidden by default;
- semantic event namespace and category fallback;
- target-specific event filtering;
- Dreame numeric OGG `tar.gz` builds;
- classic Roborock named-WAV / `.pkg` builds;
- IJAI named-MP3 ZIP builds;
- portable non-installable semantic bundles for unknown families;
- Creator Studio `vvh.voicepack.v1`;
- desktop UI for macOS / Windows / Linux;
- privacy-safe install history and `vvh.compat-report.v1`;
- searchable public catalog;
- reproducible release bundles, SPDX SBOM and SHA256 verification;
- offline package forensics and privacy-safe evidence assessment (v0.9).

## Local app

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
vvh doctor
vvh web
```

Desktop:

```bash
pip install -e ".[desktop]"
vvh-desktop
```

## Find a model

```bash
vvh models
vvh model-info xiaomi.vacuum.d101
vvh model-info roborock.vacuum.s5
vvh model-info ijai.vacuum.v2
```

The Web UI and Creator Studio include model search.

## Check a voice without installing

```bash
vvh coverage warcraft --model xiaomi.vacuum.d101
vvh coverage maxim-full --model roborock.vacuum.s5
```

Coverage uses the canonical semantic layer and does not need to build an encrypted/vendor package.

## Build a target package

```bash
vvh build maxim-full --model dreame.vacuum.r2228o
vvh build maxim-full --model ijai.vacuum.v2
vvh build maxim-full --model xiaomi.vacuum.d101
```

Classic Roborock encrypted `.pkg` output additionally requires `ccrypt`.

## Install policy

VVH fails closed.

- X10: hardware verified.
- Known but unverified local transports: explicit `--allow-experimental-transport`.
- Newer vendor-signed Roborock: arbitrary custom install blocked.
- Unknown Xiaomi/Viomi/ROIDMI/etc transports: build/preview/coverage only.

Example experimental installation:

```bash
vvh install maxim-full \
  --model roborock.vacuum.s5 \
  --ip 192.168.1.123 \
  --credential home-robot \
  --allow-experimental-transport
```

Never treat model similarity as physical verification.

## Creator Studio

```bash
vvh web
```

Open `/creator` and build one semantic voice project for many target families.

## Community verification

```bash
vvh report --ip 192.168.1.123 --model dreame.vacuum.r2209 --credential home-x10
```

Reports omit token, IP and MAC and are never uploaded automatically.

## Public catalog and reproducible releases

```bash
vvh site build --output public
vvh site verify public

vvh release build --output release
vvh release verify release
```

See [DISTRIBUTION.md](docs/DISTRIBUTION.md).

## Credits

Every community voice entry retains its upstream source and credit metadata.

- [Credits](CREDITS.md)
- [Catalog](catalog/CATALOG.md)
- [Third-party audio policy](THIRD_PARTY_AUDIO.md)

VVH is independent community software and is not affiliated with Xiaomi, Mijia, Dreame, Roborock, IJAI, Viomi, ROIDMI, Smartmi or third-party character rights holders.
