# v1.0 stable release publication

The GitHub Actions workflow `.github/workflows/publish-stable-v100.yml`
publishes the official **source/public catalog** release tag `v1.0.0` automatically
**only** after successful `CI` on the current `main` SHA.

The workflow requires `PROJECT_STATUS.md` to declare
`SOFTWARE STABLE / SOURCE SEALED` and package version `1.0.0`, re-runs
model/locale/alias and source integrity audits, builds and verifies its own
deterministic catalog/release bundle, then uses GitHub's scoped
`GITHUB_TOKEN` with contents-write to create the **single** official GitHub release.
It refuses stale main, existing tags without a matching release and duplicate
publication, and never overwrites an existing release.

- Artifacts: public catalog ZIP, `release-manifest.json`,
  `update-feed.json`, `SHA256SUMS`, SPDX SBOM and GitHub
  auto-generated source archives. No third-party audio or firmware binaries.
- No GitHub user credentials, personal robot information or deployment
  passwords are handled by this workflow.
- Desktop binaries are **not** attached or claimed signed/notarized. Exact
  feature PR head previously passed Windows/macOS/Linux packaging.
- Does not prove custom voice installation on untested devices. The only
  physically verified VVH custom voice install target remains Xiaomi X10.
- Should contents-write be restricted by organization/repository policy, the
  workflow fails closed and release publication remains **pending**, with
  stable tested source still available in main. Never claim publication
  before the GitHub Release endpoint confirms it.

This publisher is intentionally version-specific. Future releases must
introduce their own reviewed version/compatibility/release contract; this
workflow cannot silently republish or retag v1.0.0 on a later v1.x commit.
