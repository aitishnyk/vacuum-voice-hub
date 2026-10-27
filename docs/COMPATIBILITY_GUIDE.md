# Read compatibility correctly

The public catalog is generated from canonical repository data. All 223 IDs
and aliases are preserved. Search by manufacturer, marketing name, canonical
ID or alias. Filter evidence level, sort, export visible CSV, or link to a
model's `#model-CANONICAL_ID` anchor.

| Label | What it means |
| --- | --- |
| Hardware Verified | Physical custom-voice installation evidence exists for the exact model; examine documented firmware. |
| Experimental Transport | A transport implementation exists but custom installation is not guaranteed. |
| Build / Preview Only | Local audio work or offline packages; installation is not verified. |
| Unsupported / Vendor Restricted | Firmware signing or vendor restrictions prevent confirmed custom installation. |

Only Xiaomi X10 (`dreame.vacuum.r2209`) is physically verified in VVH. A model
profile, event map, successful package build or working stock package does not
prove custom-voice installability. Unknown evidence is displayed as unknown,
never promoted. Names and manufacturers follow catalog attribution and may
represent regional branding; a similar marketing name is not a hardware match.

Public fields include IDs, aliases, adapter/family, event profile, audio format,
container, build availability, default install policy, transport evidence,
tested firmware and limitations. Voice preview requires a legally available
local recording. Third-party catalog entries do not bundle preview audio.

For actual hardware research, follow [Hardware testing](COMMUNITY_HARDWARE_TESTING.md).
Do not publish tokens, local addresses, MACs or private firmware dumps.
