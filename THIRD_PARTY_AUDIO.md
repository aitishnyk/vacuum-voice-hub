# Third-party audio policy

The **VVH source code and original metadata** are MIT-licensed. That does **not** automatically license voice clips from films, games, cartoons, celebrities or other community packs.

Therefore the public repository follows these rules:

1. Do not commit third-party character audio merely because it is downloadable elsewhere.
2. Prefer an upstream/source URL plus integrity hash and an adapter recipe.
3. Mirror audio only when the source has an explicit redistribution license compatible with mirroring.
4. Keep credits and source links visible in the UI and CLI.
5. Honor takedown/removal requests promptly.
6. User-imported local packs remain local unless the user has the right to redistribute them.

The catalog field `redistribution` is one of:
- `allowed` — upstream license explicitly permits redistribution;
- `source-only` — install by fetching from upstream; VVH should not mirror it;
- `unknown` — do not mirror until clarified.
