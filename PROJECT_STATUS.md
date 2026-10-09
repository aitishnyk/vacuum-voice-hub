# Project status — v0.20.0 source candidate

- Base: v0.19.0 SOURCE SEALED, main `4bc3a534dd71bb9aef56eb6c94341a5b1327a243`.
- Scope: 223 researched model identities (8 newly added, build/preview-only); 55 original attributed voice variants; 22 text-only 16-event locales (4 new).
- Audio: `vvh creator master-preview` creates separate offline WAV with silence trimming, padding, bounded peak adjustment and fades. Source files and Creator manifests are never automatically modified. Human listening and rights clearance remain required.
- Community-first testing: accept voluntarily submitted exact model/firmware playback/reboot/rollback reports; optional manufacturer or community loan/donation of robots, **no endorsement or shipping promised**. Testing unavailable hardware is not a prerequisite to a stable software release.
- Physical installation: only Xiaomi X10 (`dreame.vacuum.r2209`) has VVH on-device custom-voice acceptance. New models have `unsupported-local` transport; offline semantic build cannot certify actual event mappings or firmware installation.
- v0.20.0 is **not yet SEALED**: exact-head Python tests, matrix, public site, release bundle, CodeQL and three-OS desktop CI still require completion.
- Commercial Telegram/Stars/Bunny functionality remains outside this repository.

See [community testing](docs/COMMUNITY_HARDWARE_TESTING.md) and [audio mastering](docs/AUDIO_MASTERING_V020.md).
