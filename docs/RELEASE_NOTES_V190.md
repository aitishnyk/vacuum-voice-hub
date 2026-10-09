# v1.9.0 — Creator Recovery and Desktop Safety

This software increment adds a fully local Creator Studio recovery
workflow: deterministic ZIP backups of only assigned audio, independent
manifest/audio SHA-256 verification, source snapshot comparison, and
new-directory-only restore with rollback of unsuccessful restores.

All operations use bounded input/output and explicit non-overwrite
behavior. Malicious archive paths, duplicate names, symlinks and tampered
audio are refused. The source project is never rewritten by recovery.

The recovery archive contains **private voice recordings and project
metadata**. It is not a public release artifact, encryption system,
copyright license or proof of a signed vendor install path.

This source release preserves 223 researched model identities,
55 attributed prerecorded variants, >=22 text-only script locales and
Xiaomi X10 as the sole VVH hardware-verified custom-install target.
Windows/macOS/Linux packaging acceptance is separate from operating
system code signing/notarization, which this release does not claim.
