# Project status — v1.7.0 SOFTWARE STABLE (source)

This source increment adds the **offline, non-executable adapter
interchange SDK**: a strict descriptor parser, exact canonical robot
model/semantic IDs, safe user-owned archive build and deterministic
SHA-256 verification. It does not create official vendor voice packages
or allow any additional robot/firmware installation.

Production and release acceptance are separate: successful PR CI,
CodeQL, catalog/source audits, source bundle, public site, Windows/macOS/
Linux desktop builds and the exact merged-main GitHub Release workflow.

Protected baseline: 223 researched model identities, 55 credited
voice variants, at least 22 text-only script locales; only
Xiaomi X10 is independently VVH hardware tested.
Redistribution rights, native-language fluency and manufacturer
signature verification are not automatically established. Public
catalog ZIP contains metadata only, not licensed prerecorded voices
or signed desktop installers.

See [adapter guide](docs/ADAPTER_INTERCHANGE_V170.md)
and [roadmap](https://github.com/aitishnyk/vacuum-voice-hub/issues/55).
