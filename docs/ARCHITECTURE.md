# Architecture

VVH separates **voice sources**, **source formats**, **canonical event semantics**, and **target models**.

```text
upstream voice pack
   ↓ verify
source-format adapter
   ↓ semantic event IDs
canonical Dreame event space
   ↓ target model adapter
model-specific audio/package format
   ↓ transport adapter
robot
```

For `dreame.vacuum.r2209`, current community packs are normalized to numeric `.ogg`, Ogg Vorbis, 16 kHz, mono and packed into a flat `tar.gz`. Installation uses local miIO/MIoT property `siid=7, piid=4` and polls `piid=3`.

The project intentionally keeps model-specific behavior in `vacuum_voice_hub/models/` so future robots can use different file formats, event maps or transports without forking the catalog.
