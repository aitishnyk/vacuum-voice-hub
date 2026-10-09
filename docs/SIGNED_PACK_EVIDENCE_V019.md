# v0.19.0 — Signed Whole-Pack Provenance and Firmware Evidence Bundle

This release extends the existing offline per-clip Ed25519 reviewer attestations. It is **software and research evidence only**, never a newly granted manufacturer voice-upload transport or approval to redistribute an audio recording.

## Sign all assigned voice clips together

Install the optional cryptography backend for plain Python CLI:

```bash
python -m pip install 'vacuum-voice-hub[review-signing]'
```

Use an **already-owned**, locally protected Ed25519 private PEM key, not a key imported from an untrusted reviewer:

```bash
vvh creator review sign-pack ./review.json \
  --private-key ./reviewer-private.pem \
  --require-approved \
  --output ./signed-pack.json

vvh creator review verify-pack ./signed-pack.json \
  --public-key ./reviewer-public.pem \
  --review ./review.json
```

The versioned `vvh.signed-pack-manifest.v1` records each assigned semantic, its exact numeric model event IDs, relative source audio path, SHA-256 and byte length, supplied translation, reviewer state, claimed reviewer name, date and explicit language/rights claims. It additionally binds the model ID, pack ID, selected locale, Creator manifest SHA-256 and script digest. The signature protects the entire manifest, including the signed creation time. Verification checks both the Ed25519 signature and **every current local source audio recording**, corresponding review state and script/manifest fingerprint.

`--require-approved` refuses to sign if any *assigned* recording is not explicitly approved by its local human reviewer. With the flag omitted, a partially recorded or reviewed voice pack can be signed as a **draft with transparent counts**, not presented as human-approved.

The tool never writes to a Creator audio source or stores/private-uploads the key. A valid signature only proves **possession of the supplied key**, not a verified person's real identity, rights to reproduce voices, spoken-language correctness or firmware-install capability.

## Collect and verify exact candidate firmware evidence, without including the package

Prepare a separate small `vvh.hardware-acceptance.v1` JSON report for one canonical model and firmware version. It must contain a genuine candidate package's local SHA-256 and byte size plus five explicit research observations — manufacturer signature review, download, audio playback, reboot persistence and tested stock rollback — each backed by a URL if marked true.

```bash
vvh research evidence-bundle ./hardware-report.json \
  --package ./candidate.pkg \
  --output ./hardware-evidence.zip

vvh research verify-evidence-bundle ./hardware-evidence.zip \
  --package ./candidate.pkg \
  --model roborock.vacuum.a75
```

Before creating or verifying the archive, the tool reads the **local package** and compares its actual SHA-256 and byte size with the claims. The ZIP contains precisely `evidence.json`, `assessment.json` and `manifest.json` — **no firmware binary, robot token, local package filepath or secret**. It rejects modified assessment/manifest content, extra ZIP members and changed source package data.

The output is never a physical installation certificate. Even five reported successful tests return `ready-for-independent-hardware-review` and `install_authorized=false`. Another person must verify the evidence and physically test exact device/firmware/rollback before any new install path may become supported. Do not share candidate proprietary firmware unless licensed.

## Preservation and testing

```bash
python -m pytest -q
python scripts/model_matrix_audit.py
vvh creator review sign-pack --help
vvh research evidence-bundle --help
vvh release build --output release
vvh release verify release
```

Preserved: **215 exact canonical model identities and aliases**, all **55 credited voice variants**, **18 text-only script locales**, historical 109/154 ID/route fixtures and Xiaomi X10 (`dreame.vacuum.r2209`) as the only physically verified VVH custom voice installation target. All signed newer hardware stays research/build-only, no region unlock or signature bypass.
