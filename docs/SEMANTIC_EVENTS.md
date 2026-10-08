# Semantic events — `vvh.semantic.v1`

v0.3 introduces a model-independent semantic layer above raw Dreame numeric event IDs.

Examples:

| Raw ID | Semantic event | Category |
|---:|---|---|
| 7 | `clean.start` | cleaning |
| 11 | `clean.pause` | cleaning |
| 12 | `clean.complete` | cleaning |
| 13 | `dock.return.charge` | dock |
| 35 | `error.main_brush` | error |
| 36 | `error.side_brush` | error |
| 43 | `error.bumper` | error |
| 45 | `locate.here` | other |
| 47 | `dock.charge.start` | dock |
| 82 | `mapping.start` | mapping |
| 84 | `mapping.complete` | mapping |
| 110 | `base.auto_empty.start` | base |

The union catalog currently covers at least **560 numeric IDs** observed across the v0.3 model profiles.

Common events receive curated stable semantic names. Model-specific or ambiguous IDs remain `dreame.event.<id>` until reviewed instead of being given a guessed meaning.

## Category fallback

A voice pack can be supplemented selectively:

```bash
vvh build warcraft \
  --model dreame.vacuum.r2228o \
  --fallback-category error=q0-russian \
  --fallback-category dock=q0-russian \
  --fallback uk-female-pensive
```

Order:
1. primary voice;
2. category-specific fallback packs;
3. general fallback;
4. missing events remain missing.

Only IDs present in the selected model profile may enter the generated package.

This prevents a modern 500+ event X40/L40 pack from blindly injecting unknown IDs into an older model.
