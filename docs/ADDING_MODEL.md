# Adding a robot model

Create a model adapter under `vacuum_voice_hub/models/` and register it in `models.json`.

A model adapter defines:
- exact model identifiers;
- audio codec/sample rate/channels;
- package container/filename rules;
- mapping from canonical event IDs to target event IDs if required;
- installation transport and status properties;
- minimum supported firmware notes;
- whether installation was verified on physical hardware.

Never mark a model `device_tested=true` without a real-device log showing download and successful activation.
