#!/usr/bin/env bash
# Owner-only ONE-SHOT GitHub Actions runner on macOS.
# Exact runner release + SHA-256, random job-specific label, no default labels.
# No persistent service, no fork/PR trigger, no release upload.
set -Eeuo pipefail
umask 077

REPO="aitishnyk/vacuum-voice-hub"
WORKFLOW="v2-owner-macos-once.yml"
RUNNER_VERSION="2.338.0"
case "$(uname -s):$(uname -m)" in
  Darwin:arm64)
    ARCH=arm64
    PACKAGE_SHA256="df4cebda25c86a886ed204e49fee63f5c2e7cec5f447b5c98440a826bbdf9df2"
    ;;
  Darwin:x86_64)
    ARCH=x64
    PACKAGE_SHA256="dea7a58796ce215fc424a8b27c0fdd9b813fa5fc03d109a4a1d38131d6bfa1a3"
    ;;
  *)
    echo "ERROR: Mac running macOS arm64 or x86_64 required." >&2
    exit 2
    ;;
esac
for cmd in gh curl shasum tar openssl git python3.12; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: missing $cmd" >&2
    exit 2
  }
done
gh auth status -h github.com >/dev/null 2>&1 || {
  echo "ERROR: run 'gh auth login' before starting" >&2
  exit 2
}
GH_LOGIN="$(gh api user --jq .login)"
if [[ "$GH_LOGIN" != "vbrekher" ]]; then
  echo "ERROR: authenticate gh as vbrekher (got $GH_LOGIN)." >&2
  exit 2
fi

EXPECTED_SHA="$(gh api "repos/$REPO/git/ref/heads/main" --jq .object.sha)"
# Ensure that the merged main contains the specific, reviewed manual workflow.
gh api "repos/$REPO/contents/.github/workflows/$WORKFLOW?ref=$EXPECTED_SHA" --jq .sha >/dev/null
ROOT="$(mktemp -d "${TMPDIR:-/tmp}/vvh-v2-once.XXXXXX")"
cd "$ROOT"
cleanup() {
  local status="$?"
  trap - EXIT
  if [[ -f "$ROOT/.runner" ]]; then
    local remove_token
    remove_token="$(gh api -X POST "repos/$REPO/actions/runners/remove-token" --jq .token 2>/dev/null)" || remove_token=""
    if [[ -n "$remove_token" ]]; then
      "$ROOT/config.sh" remove --unattended --token "$remove_token" >/dev/null 2>&1 || true
    fi
  fi
  cd "$HOME"
  rm -rf "$ROOT"
  if [[ "$status" -ne 0 ]]; then
    echo "Runner exited with error $status. No persistent runner service installed." >&2
  fi
  exit "$status"
}
trap cleanup EXIT

RUNNER_FILE="actions-runner-osx-$ARCH-$RUNNER_VERSION.tar.gz"
RUNNER_URL="https://github.com/actions/runner/releases/download/v$RUNNER_VERSION/$RUNNER_FILE"
echo "Downloading official GitHub Actions runner $RUNNER_VERSION for macOS $ARCH"
curl --fail --location --retry 3 --silent --show-error --output "$RUNNER_FILE" "$RUNNER_URL"
printf '%s  %s\n' "$PACKAGE_SHA256" "$RUNNER_FILE" | shasum -a 256 -c -
tar -xzf "$RUNNER_FILE"
rm "$RUNNER_FILE"

LABEL="vvh-v2-once-$(openssl rand -hex 12)"
NAME="vvh-v2-macos-$(openssl rand -hex 6)"
echo "Registering single-use macOS runner $NAME"
# The GitHub registration token stays on this Mac only; never print it.
REG_TOKEN="$(gh api -X POST "repos/$REPO/actions/runners/registration-token" --jq .token)"
./config.sh --unattended \
  --url "https://github.com/$REPO" \
  --token "$REG_TOKEN" \
  --name "$NAME" \
  --labels "$LABEL" \
  --no-default-labels \
  --work "_work" \
  --ephemeral \
  --disableupdate
unset REG_TOKEN

echo "Dispatching exact main $EXPECTED_SHA, owner-only workflow"
gh workflow run "$WORKFLOW" \
  --repo "$REPO" \
  --ref main \
  --field "expected_sha=$EXPECTED_SHA" \
  --field "runner_label=$LABEL"

echo "Runner is now receiving ONE GitHub Actions job; do not close Terminal."
echo "Workflow page: https://github.com/$REPO/actions/workflows/$WORKFLOW"
echo "If no job is assigned, press Ctrl+C and inspect Actions / repo access."
./run.sh --once
echo "One-shot runner finished; ephemeral registration will be removed."
