# Community hardware tests and voluntary robot contributions

Vacuum Voice Hub treats **software stability** and **physical robot compatibility** as separate tracks. We welcome volunteers who can test on their own robots, and manufacturers/distributors/users who may voluntarily loan or donate hardware. No manufacturer sponsorship or hardware contribution is required for a stable software release.

## A software release is not a device-install guarantee

Automated Python tests, catalog preservation, CodeQL, package builds and Windows/macOS/Linux desktop CI establish software quality. They do not establish that a voice pack can be installed on a particular robot. At present VVH has physical custom-install verification only for Xiaomi X10 (`dreame.vacuum.r2209`). Each other device retains its own experimental, signed-only or build-only status.

## How to submit an exact-device result

1. Open a [community hardware test issue](../.github/ISSUE_TEMPLATE/community-hardware-test.md). Include exact canonical model ID, manufacturer, firmware version, country/region and event-format source.
2. Inventory a legally obtained candidate **offline** with `vvh research inspect <package> --model <model-id>` and provide a metadata-only redacted evidence report with the actual SHA-256 and size.
3. Describe transfer/download status, whether custom audio actually played, whether it persisted after a reboot, and whether **factory stock voice rollback worked**. Include reproducibility and failures, not merely one success response from an API.
4. Link redacted evidence (screenshots or logs only after removing personal/device details). A maintainer can inspect it and request independent reproduction.
5. A compatibility promotion requires an **explicit separate PR**, negative regression tests and maintainer review. Self-reported evidence never silently enables installation.

**Do not post robot/cloud tokens, serial numbers, IP/MAC addresses, account names, Wi-Fi credentials, personal addresses, signed vendor firmware, illegal bypasses, unlicensed audio or private download links.** Test only devices you own or are authorized to inspect. Keep manufacturer signing requirements intact. There is no automatic firmware modification or region unlock.

## Loans, donations and manufacturer relationships

Use a [device contribution issue](../.github/ISSUE_TEMPLATE/device-contribution.md) to identify the **model and general country only**, and state whether it is a voluntary donation or a proposed loan. Agree privately on shipping, loan duration, insurance, customs responsibility and stock condition **before** dispatching any device. No public home address or shipping details in issues. Maintainers may decline for logistical/safety reasons.

Receiving hardware does **not** guarantee support, preferential treatment, positive test results, promotion or endorsement. Sponsorship/conflicts should be disclosed, and credits are optional and consent-based. Report negatives as prominently as positives. Vendor firmware and third-party audio rights remain with their respective owners.

## Language and audio reviews

The 22 built-in locales are **text reference scripts**, not recorded voice libraries. Community native speakers are welcome to review each phrase, naturalness, locale and accessibility. Generated audio also needs human listening and separate redistribution clearance. Use Creator Human Review and signed-pack provenance; machine-generated signal scores alone do not prove language or legal rights.

We will continue shipping source-compatible releases without waiting for every model to be physically donated or tested. Models lacking physical evidence remain clearly marked build-only or research-only.
