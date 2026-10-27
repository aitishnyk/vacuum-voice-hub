# Developer guide — v2.1

Use Python 3.12. The existing architecture is retained: `catalog/` is canonical,
`vacuum_voice_hub/data/` is packaged catalog data, `models/` contains adapters,
`creator.py` implements project workflows, `server.py` owns the loopback API,
`web/` the local UI, and `sitegen.py` generates the public catalog.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[desktop,review-signing]' pytest pyinstaller pillow cairosvg
python -m pytest -q
python scripts/model_matrix_audit.py
python scripts/stable_release_audit.py
python scripts/v2_release_acceptance.py --compatible
python scripts/v21_release_acceptance.py
python scripts/check_web_js.py
python -m compileall -q vacuum_voice_hub
vvh --help
vvh site build --output public
vvh site verify public
python scripts/fetch_codec_sources.py --output work/codec-source
sh scripts/build_codec.sh work/codec-source
export VVH_FFMPEG="$PWD/work/codec-source/runtime/bin/ffmpeg"
export VVH_CODEC_NOTICES="$PWD/work/codec-source/NOTICES"
python scripts/build_sbom.py --output work/SBOM.json --notices work/codec-source/NOTICES
python scripts/build_desktop.py
```

`v2_release_acceptance.py` defaults to the historical exact 2.0.0 check;
`--compatible` preserves its feature and safety invariants on later v2 releases.
Historical publication workflows and v2.0.0 assets remain unchanged.

Desktop builds must run on each target OS and architecture. Build output is
unsigned and untested until a separate platform report proves otherwise.
`VacuumVoiceHub --smoke-test /absolute/report.json` checks bundled FFmpeg,
demo processing/export, native page loading and server shutdown. It does not
prove audible native playback. Complete the owner checklist in
[Platform acceptance](PLATFORM_ACCEPTANCE.md) before advertising downloads.

Regenerate synthetic audio with `python scripts/generate_demo.py` (eSpeak NG
1.52.0 required). Run `python scripts/generate_brand.py` for original brand
assets. Do not include external voices, TTS weights or packs without a license.
FFmpeg's build configuration and redistribution license must be recorded for
any binary published; include applicable GPL notices and matching source offer.

Add adapters using [Adding a model](ADDING_MODEL.md), preserving canonical IDs,
aliases and default-deny install policies. Review [Contributing](../CONTRIBUTING.md)
and [Security](../SECURITY.md). Release only from an exact reviewed commit;
record build SHA, dirty state, file size, checksums, SBOM, signing status,
platform evidence and downloaded-asset verification independently.
