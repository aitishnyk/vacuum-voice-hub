# v1.7.0 — Offline Adapter Interchange SDK

This source/software increment adds an actual, deterministic Creator
interchange builder and archive verifier via `vvh adapter`.

- Versioned `vvh.adapter-descriptor.v1` source descriptor for exact
  canonical models and known semantic events.
- Fully offline `preflight`, `build`, `verify` with SHA-256 binding
  of descriptor, Creator project manifest and all archive audio.
- Portable ZIP build of 1–128 user-supplied clips, strict encoding/filename
  validation, symlink prevention, 25 MiB/clip and 100 MiB aggregate limits.
- Never executes third-party plugin code, changes device transport policy,
  claims rights, or builds a signed manufacturer-specific device package.

Baseline 223 source-attributed model profiles, 55 credited variants,
>=22 text-only script locales and Xiaomi X10-only physical verification
preserved. Public source archive contains metadata/catalog; it does not
include community voice assets or signed desktop installers.
