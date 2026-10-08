# Public Catalog / Website

Vacuum Voice Hub v0.6 can generate a static public website and machine-readable catalog directly from the canonical repository data.

## Build

```bash
vvh site build --output public
vvh site verify public
```

Output:

```text
public/
├── index.html
├── catalog.json
├── models.json
└── manifest.json
```

## Public data contract

The manifest schema is `vvh.public-catalog.v1`.

`catalog.json` contains public voice metadata:
- ID and title;
- language and 18+ marker;
- tags;
- credit;
- source page;
- origin model/family;
- format;
- source verification;
- redistribution policy.

Raw download/integrity internals are intentionally not required by the public browser catalog.

`models.json` contains:
- canonical model ID and aliases;
- event profile and event count;
- profile evidence type;
- transport evidence type;
- whether normal local install is allowed;
- hardware-verification state.

## Integrity

`manifest.json` stores SHA-256 digests for `catalog.json` and `models.json`.

`vvh site verify` recomputes those hashes and fails on tampering.

The build intentionally omits timestamps so identical source data and VVH version produce byte-identical catalog/model/manifest files.

## Static site

The generated `index.html` provides:
- voice search;
- language filter;
- 18+ opt-in;
- source/credit links;
- model compatibility cards;
- explicit hardware-verification labels.

No backend is required.

## CI artifact

`.github/workflows/public-site.yml` builds, verifies and uploads `VacuumVoiceHub-Public-Site` on relevant pull requests, main pushes and manual runs.

The artifact is GitHub-Pages-ready. Deployment can be enabled independently without changing the site format.

## Privacy

The public generator reads only canonical catalog/model data. It does not read:
- local install history;
- compatibility reports;
- Creator workspaces;
- credentials;
- tokens;
- local IP/MAC data.
