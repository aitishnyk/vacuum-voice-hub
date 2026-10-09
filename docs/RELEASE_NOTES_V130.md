# v1.3.0 — Local Pronunciation Lexicon

This public software-stable source increment introduces an optional local
language-specific pronunciation dictionary for the installed Piper and
eSpeak TTS engines. It performs literal one-pass replacements without
modifying original localized script text.

- New `scripts pronounce` preview.
- Opt-in `--lexicon` for offline `scripts piper` and `scripts synth`.
- Bounded local file, user attribution, license, exact SHA-256 provenance,
  duplicate/symlink/invalid UTF-8 prevention and one-pass substitutions.
- PR #57 exact functional head: **287 Python tests PASS**, model matrix,
  source audit, CodeQL, Public Site, Release Bundle, Windows/macOS/Linux.

Boundaries: retained 223 researched model identities, 55 credited voice
variants and >=22 **text-only** locales. Xiaomi X10 alone is physically
verified VVH custom-voice target. No certified additional install paths.
Human pronunciation, speaker licensing and platform code signing not
independently verified. Public archive contains metadata/catalog, not
licensed voice recordings or signed desktop installers. Broader v1.3
semantics/native review and v1.4–v2.0 work remain pending.
