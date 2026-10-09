# Project status — v1.9.0 SOFTWARE STABLE (source)

The v1.9 software increment adds a **real offline Creator backup/restore
workflow**: deterministic ZIP of an existing project's explicitly assigned
audio and manifest, SHA-256 checks for every member, verification,
comparison with live source, and safe restore to a **new directory**.
Restore never overwrites or mutates existing Creator workspaces.

These private user backups **contain actual voice audio** and are
neither encrypted nor remotely uploaded. Public GitHub release assets
are still source/catalog metadata only. Archive checksums are not a
copyright license, digital signature or manufacturer-endorsed install.

Source-stable acceptance requires independent PR regression, CodeQL,
public site and bundle, Linux/macOS/Windows packaging, historical model
preservation audit and successful merged-main CI + version-specific
official GitHub Release. Platform code signing/notarization are not
claimed without external signing infrastructure.

Baseline: 223 researched model identities, 55 credited variants,
>=22 text-only script locales and Xiaomi X10 as VVH's sole physically
verified custom-voice install target. No new transport authorization.
See [guide](docs/CREATOR_RECOVERY_V190.md)
and [roadmap](https://github.com/aitishnyk/vacuum-voice-hub/issues/55).
