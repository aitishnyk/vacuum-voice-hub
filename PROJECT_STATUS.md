# Project status — v1.2.0 SOFTWARE STABLE (source)

The v1.2.0 functional increment was merged to main through
[PR #54](https://github.com/aitishnyk/vacuum-voice-hub/pull/54)
at `0f950a24e86e1626f268b9245c1d17a0c93dc3c0`. Exact PR-head CI: **275 Python tests PASS**, CodeQL, Public
Site, Release Bundle, Windows/macOS/Linux desktop package jobs all PASS.

The source adds copy-on-write language review backed by script SHA-256
snapshots and offline read-only audio A/B measurements.
This does **not** independently certify language, voice rights, any new
robot hardware/firmware install path or desktop executable signatures.

Baseline protected: 223 model identities, 55 attributed variants,
>=22 **text-only** locales; Xiaomi X10 alone marked hardware tested.

Release publication is carried out separately through GitHub Actions;
do not infer an official release from this file alone. Follow
[GitHub Releases](https://github.com/aitishnyk/vacuum-voice-hub/releases)
for exact assets and immutable tags.

Commercial Telegram/Stars/Bunny code remains outside this repo.

Remaining v1.3-v2.0 scope is tracked in
[issue #55](https://github.com/aitishnyk/vacuum-voice-hub/issues/55).
