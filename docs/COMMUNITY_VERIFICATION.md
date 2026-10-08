# Community Verification

Vacuum Voice Hub uses `vvh.compat-report.v1` for privacy-safe model verification reports.

## Create a live report

```bash
vvh report --ip 192.168.1.123 --model dreame.vacuum.r2209
```

With a token stored in the OS secret store:

```bash
vvh report --ip 192.168.1.123 --model dreame.vacuum.r2209 --credential home-x10
```

The report is saved locally under the VVH data directory.

## What the report contains

- VVH version;
- operating system / architecture / Python version;
- robot model;
- firmware and hardware strings;
- event-profile identity and size;
- transport evidence level;
- current voice ID/state/progress when readable;
- latest sanitized local install result;
- whether the evidence qualifies as a **hardware-evidence candidate**.

## What is intentionally excluded

- MIIO token;
- IP address;
- MAC address;
- local HTTP download URL;
- any credential-store data.

Reports are validated before writing. A 32-hex secret-like value, IPv4 address or forbidden privacy key causes validation to fail.

## Hardware verification rule

A report may set `hardware_evidence_candidate=true` only when:

1. local install history shows success;
2. the robot itself downloaded the package;
3. install state reached `success / 100%`;
4. the live robot still reports `success / 100%`.

This is evidence for review, not an automatic edit to the public model catalog. A maintainer must review the report before changing `device_tested` / `hardware_verified`.

## Validate a received report

```bash
vvh validate-report compat-report-....json
```

The authoritative schema is `schemas/vvh.compat-report.v1.schema.json`.
