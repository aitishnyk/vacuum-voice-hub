# v0.18 — Signed Reviewer Provenance, Audio QA & Device Evidence UX

This is an **offline software workflow** built on v0.17's source-checked Creator review checklists. It preserves the distinction between what a human attests, what cryptography proves, what simple signal statistics measure, and what a physical robot actually accepts.

## 1. User-controlled Ed25519 review signing

Install the optional component for a bare Python CLI:

```bash
python -m pip install 'vacuum-voice-hub[review-signing]'
```

The user independently generates, stores and secures an **Ed25519 PEM key pair**. VVH **never** generates or retains private keys on its servers or in the Creator project. Only use keys whose provenance and ownership you have separately confirmed. After a real local human review has reached `approved` with named reviewer and explicit language/rights claims:

```bash
vvh creator review attest ./review.json \
  --semantic clean.start \
  --private-key ./reviewer-ed25519-private.pem \
  --output ./clean-start-attestation.json

vvh creator review verify-attestation ./clean-start-attestation.json \
  --public-key ./reviewer-ed25519-public.pem \
  --review ./review.json
```

The detached `vvh.reviewer-attestation.v1` binds the exact canonical model, pack, locale, semantic, numeric event IDs, audio SHA-256 and bytes, translation-script digest, Creator manifest digest, human reviewer name and review timestamp, explicit language and rights statements, and creation timestamp. The signature verifies with the **public** key and current review/audio hashes. A different public key, changed audio, altered translation or modified signed payload invalidates verification. Existing output files are never overwritten.

**What is NOT proved:** reviewer real-world identity, the author's rights to use a particular voice, copyright transfer, linguistic quality or safety of uploading to a device. An Ed25519 signature proves possession of a matching private key when the attestation was made, nothing more. Keep the private key outside shared review ZIPs.

## 2. Compare human review and bounded engineering-quality signal statistics

```bash
vvh creator review audio-acceptance ./review.json --max-clips 16
vvh creator review audio-acceptance ./review.json \
  --max-clips 16 --decode-compressed
```

This read-only `vvh.review-audio-acceptance.v1` report combines **independent** columns: source audio SHA, current human review status, declared rights assertion, and bounded WAV/optional FFmpeg signal metrics (RMS, peak, clipping, silence and duration warnings). The report processes only 1–32 clips per invocation and states the number not processed. It never modifies original audio, does not assert the spoken language, and cannot transform its own signal result into `approved`.

Creator Studio's **Audio & Human QA** button shows the same report; optional compressed decoding is user-controlled. The default keeps costly compressed decoding off.

## 3. Firmware / robot evidence questionnaire

The new Creator Studio panel accepts:
- exact catalog model ID;
- specific firmware version;
- **SHA-256 and actual byte size** of a candidate package;
- five yes/no observations plus public evidence links, for a signature review, device download, audible playback, persistence after reboot, and working stock-voice rollback.

Nothing is uploaded to the robot, no real credentials are read, and there is no automatic region unlock. Results remain either `incomplete-research-only` or `ready-for-independent-hardware-review`, both **install_authorized=false**. Self-reported evidence has no power to enable an unverified model installer. Keep independent hardware/firmware tests tracked in [Issue #14](https://github.com/aitishnyk/vacuum-voice-hub/issues/14).

## 4. Build and acceptance boundaries

```bash
python -m pytest -q
python scripts/model_matrix_audit.py
python scripts/check_web_js.py
vvh release build --output release
vvh release verify release
```

CI installs the optional `review-signing` extra to test real Ed25519 key signing, wrong-key rejection, modified-signed-payload rejection and source-audio fingerprint changes. Desktop builds for macOS, Windows and Linux include this module, whereas base Python CLI installation does not make it mandatory.

All **215 previous canonical model IDs and aliases**, **55 source-attributed voice identities** and **18 built-in text-only locale scripts** remain unchanged; historical 109/154 identity fixtures remain frozen. Xiaomi X10 (`dreame.vacuum.r2209`) continues to be the sole VVH-hardware-tested custom-voice target. The broader software model matrix never implies 215 custom voice installation paths.
