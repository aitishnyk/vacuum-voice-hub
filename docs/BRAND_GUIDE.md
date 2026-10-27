# Vacuum Voice Hub identity

**Give your robot vacuum a voice.**

The original circular robot outline contains a cyan/violet voice waveform.
The master is `vacuum_voice_hub/brand/master.svg`. Use icon variants at 32 px
or larger and the horizontal wordmark where the name needs context. Keep clear
space of at least one quarter of the icon width; preserve proportions, contrast
and the waveform. Do not combine it with a manufacturer logo or imply endorsement.

Palette: Deep Navy `#0B1220`, Electric Cyan `#22D3EE`, Violet `#A78BFA`,
Surface `#162235`, Light Text `#F8FAFC`. Cyan buttons use navy text.
Typography: native system sans-serif, with system monospace for hashes and IDs.
Do not download fonts. Body text starts at 14–16 px; controls use visible focus.
Spacing follows an 8 px rhythm; surfaces have 16–24 px padding.

Run `python scripts/generate_brand.py` with CairoSVG and Pillow to regenerate
SVG variants, transparent PNGs, favicon, Windows ICO, macOS ICNS and the
1200×630 social card. Linux uses `icon-512.png`. All identity artwork is original
and covered by the repository MIT license. Social artwork is a brand composition,
not a product screenshot. Screenshots in `docs/assets/screenshots` capture the
running application and are separately described in their capture notes.
