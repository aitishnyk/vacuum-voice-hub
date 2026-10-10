#!/usr/bin/env bash
# Manual, owner-approved v2.0.0 public SOURCE release.
# This does not claim CodeQL/Windows/Linux/hardware validation.
set -Eeuo pipefail
umask 077
REPO="aitishnyk/vacuum-voice-hub"
VERSION="v2.0.0"
ACCEPTED_SHA="419ca0033874b11ee60915c4a6a3be5ae0c094f2"
MAC_RUN="38089303529"
EPOCH="1700000000"

for program in gh git python3.12 shasum cmp; do
  command -v "$program" >/dev/null 2>&1 || { echo "Missing: $program" >&2; exit 2; }
done
gh auth status -h github.com >/dev/null 2>&1 || { echo "Run gh auth login" >&2; exit 2; }
[[ "$(gh api user --jq .login)" == "vbrekher" ]] || { echo "Wrong GitHub owner account" >&2; exit 2; }
if gh release view "$VERSION" --repo "$REPO" >/dev/null 2>&1; then
  echo "Release already exists. Never overwrite published assets."
  gh release view "$VERSION" --repo "$REPO" --json tagName,url,isDraft,isPrerelease
  exit 0
fi
if gh api "repos/$REPO/git/ref/tags/$VERSION" >/dev/null 2>&1; then
  echo "Version tag already exists without a release; refusing overwrite." >&2
  exit 3
fi

RUN_STATUS="$(gh api "repos/$REPO/actions/runs/$MAC_RUN" --jq .conclusion)"
RUN_SHA="$(gh api "repos/$REPO/actions/runs/$MAC_RUN" --jq .head_sha)"
[[ "$RUN_STATUS" == "success" && "$RUN_SHA" == "$ACCEPTED_SHA" ]] || {
  echo "Cannot verify successful macOS GitHub Actions evidence" >&2
  exit 3
}

TARGET_SHA="$(gh api "repos/$REPO/git/ref/heads/main" --jq .object.sha)"
WORK="$(mktemp -d)"
trap 'cd "$HOME"; rm -rf "$WORK"' EXIT
git clone --quiet "https://github.com/$REPO.git" "$WORK/source"
cd "$WORK/source"
[[ "$(git rev-parse HEAD)" == "$TARGET_SHA" ]] || {
  echo "Main moved during checkout; abort." >&2
  exit 3
}
git merge-base --is-ancestor "$ACCEPTED_SHA" "$TARGET_SHA" || {
  echo "Current main does not descend from the Mac-accepted SHA" >&2
  exit 3
}

# Only release documentation/this helper may differ from the exact source
# already accepted in GitHub Actions. Code/data changes require fresh QA.
while IFS= read -r changed; do
  [[ -z "$changed" ]] && continue
  case "$changed" in
    ops/release/publish-v200-source.sh|docs/V2_DELIVERY_CLOSURE.md|docs/RELEASE_NOTES_V200.md|PROJECT_STATUS.md|README.md) ;;
    *)
      echo "Unaccepted change since successful macOS source SHA: $changed" >&2
      echo "Refusing to transfer old QA evidence to changed executable source." >&2
      exit 4
      ;;
  esac
done < <(git diff --name-only "$ACCEPTED_SHA" "$TARGET_SHA")

[[ "$(python3.12 -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')" == "2.0.0" ]] || {
  echo "Wrong package version" >&2
  exit 4
}
[[ -f docs/RELEASE_NOTES_V200.md ]] || { echo "Missing release notes" >&2; exit 4; }

python3.12 -m venv "$WORK/venv"
PYPATH="$WORK/venv/bin/python"
"$PYPATH" -m pip install --quiet -e .
"$PYPATH" -m vacuum_voice_hub release build --output "$WORK/release" --source-date-epoch "$EPOCH"
# Artifact integrity operations below are not a new regression test cycle.
"$PYPATH" -m vacuum_voice_hub release verify "$WORK/release"
(cd "$WORK/release" && shasum -a 256 -c SHA256SUMS)

[[ "$(gh api "repos/$REPO/git/ref/heads/main" --jq .object.sha)" == "$TARGET_SHA" ]] || {
  echo "Main changed during preparation; abort" >&2
  exit 4
}
if gh release view "$VERSION" --repo "$REPO" >/dev/null 2>&1 ||
   gh api "repos/$REPO/git/ref/tags/$VERSION" >/dev/null 2>&1; then
  echo "Someone created the release/tag concurrently. Refusing overwrite." >&2
  exit 4
fi

echo "Publishing v2.0.0 public source/catalog at exact SHA $TARGET_SHA"
echo "Mac source QA accepted at $ACCEPTED_SHA; hosted CodeQL/Windows/Linux DEFERRED."
echo "Unsigned desktop installers, license rights and other hardware not claimed."
gh release create "$VERSION" \
  --repo "$REPO" \
  --target "$TARGET_SHA" \
  --title "Vacuum Voice Hub v2.0.0 — Universal Voice Studio (Source)" \
  --notes-file docs/RELEASE_NOTES_V200.md \
  --latest \
  "$WORK/release/VacuumVoiceHub-public-2.0.0.zip" \
  "$WORK/release/release-manifest.json" \
  "$WORK/release/update-feed.json" \
  "$WORK/release/SHA256SUMS" \
  "$WORK/release/sbom.spdx.json"

REMOTE_TAG_SHA="$(gh api "repos/$REPO/git/ref/tags/$VERSION" --jq .object.sha)"
[[ "$REMOTE_TAG_SHA" == "$TARGET_SHA" ]] || {
  echo "CRITICAL: tag target SHA mismatch!" >&2
  exit 5
}
mkdir -p "$WORK/remote"
gh release download "$VERSION" --repo "$REPO" --dir "$WORK/remote"
for name in VacuumVoiceHub-public-2.0.0.zip release-manifest.json update-feed.json SHA256SUMS sbom.spdx.json; do
  cmp "$WORK/release/$name" "$WORK/remote/$name" || {
    echo "CRITICAL: published asset differs: $name" >&2
    exit 5
  }
done
echo "GitHub Release published and 5 remote assets byte-identical."
echo "Tag SHA: $REMOTE_TAG_SHA"
gh release view "$VERSION" --repo "$REPO" --json tagName,url,isDraft,isPrerelease
