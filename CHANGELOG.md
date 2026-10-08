# Changelog

## 0.5.0 — 2026-10-08

### Desktop
- added `vvh-desktop` and `vvh desktop`;
- added native pywebview shell around the same localhost-only application;
- added PyInstaller packaging matrix for macOS, Windows and Linux.

### Community Verification
- added `vvh.compat-report.v1`;
- added privacy-safe live report creation and validation;
- report can combine current robot state with sanitized latest-install evidence;
- hardware-evidence candidate requires download confirmation plus success/100% history and live state.

### Privacy / local state
- added bounded local install history;
- token, IP, MAC and local URL keys are removed;
- secret-like 32-hex strings and IPv4 strings are redacted from free text;
- added UI actions for history and report generation.

### Credentials
- added optional OS keyring support;
- added `vvh credential save/status/delete`;
- install/detect/restore/report commands accept `--credential`.

## 0.4.0 — 2026-10-08
- Creator Studio;
- `vvh.voicepack.v1`;
- local semantic authoring and model-aware build.

## 0.3.0 — 2026-10-08
- seven model profiles;
- semantic compatibility/category fallback;
- transport evidence policy.

## 0.2.0 — 2026-10-08
- 55 attributed voice variants;
- X10 compatibility engine and fallback.

## 0.1.0 — 2026-10-08
- initial X10-focused foundation.
