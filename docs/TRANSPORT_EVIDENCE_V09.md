# v0.9 Transport Evidence Intake (initial wave)

The offline reviewer `vacuum_voice_hub.transport_evidence` accepts bounded JSON evidence using `vvh.transport-evidence.v1`. It does **not** contact the robot, query an external source, package files, mutate the model registry, or authorize installation.

Example research document (illustrative only; not device validation):

```json
{
  "schema": "vvh.transport-evidence.v1",
  "model_id": "xiaomi.vacuum.d101",
  "source": "https://example.org/research/voice-format",
  "package": {
    "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "size_bytes": 12345,
    "format": "unknown"
  },
  "observations": ["package_inspected"]
}
```

Offline Python usage:

```python
from vacuum_voice_hub.transport_evidence import inspect_file
result = inspect_file("evidence.json", expected_model="xiaomi.vacuum.d101")
assert result["install_authorized"] is False
```

Strict fields: exact model ID, HTTPS source link, SHA-256/size/format, bounded unique observation stages. Optional `hardware.firmware` accompanies device reports. Known secret-bearing field names are rejected, and file size is limited to 64 KiB. A report claiming device download and success with firmware moves only to `hardware-review-required`, never to `hardware-verified`. Independent review must inspect source reliability, complete logs, device identity and package acceptance before any model-policy change.

Run targeted tests:

```bash
python -m pytest -q tests/test_transport_evidence_v09.py
```

Future v0.9 work: add source-backed fixtures and event maps per priority family, evidence-based adapter research and device-specific transport tests. No new models are promoted by this initial intake wave.
