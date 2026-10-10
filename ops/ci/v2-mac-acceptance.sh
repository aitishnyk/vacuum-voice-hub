#!/usr/bin/env bash
# VVH v2 offline source QA. No persistent self-hosted runner, no secrets posted.
set -Eeuo pipefail
umask 077
REPO="aitishnyk/vacuum-voice-hub"
BASE_SHA="0b8d18692a8532b02d811e9eec5ba8f9d2dc07ce"
AUDIO_SHA="754d33646a815b427a3c9f4b06e0e7b47cb957cf"
PRIVACY_SHA="33c4148479dc8a0fcb032a1f90c64f5ba626b1a5"

for app in git gh; do
  command -v "$app" >/dev/null 2>&1 || { echo "Missing $app"; exit 2; }
done
gh auth status -h github.com >/dev/null 2>&1 || { echo "Run gh auth login first"; exit 2; }
[[ "$(uname -s)" == "Darwin" ]] || { echo "This script is only for macOS"; exit 2; }
PYTHON=""
for choice in python3.12 python3.13 python3.11 python3.10 python3; do
  if command -v "$choice" >/dev/null 2>&1 && "$choice" -c \
       'import sys; assert (3,10) <= sys.version_info[:2] < (3,15)' >/dev/null 2>&1; then
    PYTHON="$(command -v "$choice")"
    break
  fi
done
[[ -n "$PYTHON" ]] || { echo "Need Python 3.10–3.14; install python@3.12"; exit 2; }

ROOT="$(mktemp -d "${TMPDIR:-/tmp}/vvh-v2-mac.XXXXXX")"
LOGS="$ROOT/logs"
mkdir -p "$LOGS"
echo "Testing exact reviewed PR heads in isolated checkout: $ROOT"
echo "No remote release, daemon or modification to your existing worktrees."
git clone --quiet --no-checkout "https://github.com/$REPO.git" "$ROOT/repo"
cd "$ROOT/repo"
git fetch --quiet origin \
  "refs/pull/67/head:refs/heads/vvh-audio" \
  "refs/pull/68/head:refs/heads/vvh-privacy"
current_main="$(git rev-parse origin/main)"
audio_head="$(git rev-parse refs/heads/vvh-audio)"
privacy_head="$(git rev-parse refs/heads/vvh-privacy)"
if [[ "$current_main" != "$BASE_SHA" || "$audio_head" != "$AUDIO_SHA" || "$privacy_head" != "$PRIVACY_SHA" ]]; then
  echo "One reviewed SHA changed. Stopping before executing changed code." >&2
  printf 'main=%s\nPR67=%s\nPR68=%s\n' "$current_main" "$audio_head" "$privacy_head" >&2
  exit 3
fi
git checkout --quiet --detach "$BASE_SHA"
git -c user.name="VVH Local QA" -c user.email="local-qa@example.invalid" \
    -c commit.gpgsign=false merge --quiet --no-ff --no-edit "$AUDIO_SHA"
git -c user.name="VVH Local QA" -c user.email="local-qa@example.invalid" \
    -c commit.gpgsign=false merge --quiet --no-ff --no-edit "$PRIVACY_SHA"
MERGED_SHA="$(git rev-parse HEAD)"
"$PYTHON" -m venv "$ROOT/venv"
PYPATH="$ROOT/venv/bin/python"
STATUS_LINES=()
FAILURES=0
gate() {
  local label="$1"; shift
  local slug="${label// /-}"
  printf '\n[CHECK] %s\n' "$label"
  if "$@" >"$LOGS/$slug.log" 2>&1; then
    echo "PASS"
    STATUS_LINES+=("- $label: PASS")
  else
    FAILURES=$((FAILURES+1))
    echo "FAIL (log on Mac: $LOGS/$slug.log)" >&2
    tail -n 12 "$LOGS/$slug.log" >&2 || true
    STATUS_LINES+=("- $label: FAIL")
  fi
}
release_gate() {
  "$PYPATH" -m vacuum_voice_hub release build --output "$ROOT/release-a" --source-date-epoch 1700000000 &&
  "$PYPATH" -m vacuum_voice_hub release verify "$ROOT/release-a" &&
  "$PYPATH" -m vacuum_voice_hub release build --output "$ROOT/release-b" --source-date-epoch 1700000000 &&
  diff -qr "$ROOT/release-a" "$ROOT/release-b" &&
  (cd "$ROOT/release-a" && shasum -a 256 -c SHA256SUMS)
}
site_gate() {
  "$PYPATH" -m vacuum_voice_hub site build --output "$ROOT/public" &&
  "$PYPATH" -m vacuum_voice_hub site verify "$ROOT/public"
}
desktop_gate() {
  "$ROOT/venv/bin/pyinstaller" --noconfirm --clean --windowed --onefile \
    --name VacuumVoiceHub --collect-data vacuum_voice_hub \
    --collect-all miio --collect-all imageio_ffmpeg --collect-all webview \
    vacuum_voice_hub/desktop.py &&
  test -e dist/VacuumVoiceHub.app/Contents/MacOS/VacuumVoiceHub
}
cli_gate() {
  "$PYPATH" -m vacuum_voice_hub --version &&
  "$PYPATH" -m vacuum_voice_hub stats
}

gate "Dependencies" "$PYPATH" -m pip install -e '.[desktop,security,review-signing]' pytest pyinstaller
gate "Full-Python-regression" "$PYPATH" -m pytest -q
gate "Model-matrix-audit" "$PYPATH" scripts/model_matrix_audit.py
gate "Stable-preservation-audit" "$PYPATH" scripts/stable_release_audit.py
gate "V2-source-acceptance" "$PYPATH" scripts/v2_release_acceptance.py
gate "Python-syntax" "$PYPATH" -m compileall -q vacuum_voice_hub
gate "CLI-smoke" cli_gate
gate "Web-JavaScript-syntax" "$PYPATH" scripts/check_web_js.py
gate "Public-site-build-verify" site_gate
gate "Deterministic-release-SHA256" release_gate
gate "macOS-desktop-PyInstaller" desktop_gate
gate "macOS-installer-shell" bash -n scripts/INSTALL_MACOS.command

REPORT="$ROOT/VVH_MAC_ACCEPTANCE_SUMMARY.md"
{
  echo "### Vacuum Voice Hub v2 — macOS independent source acceptance"
  echo
  echo "- Baseline: \`$BASE_SHA\`"
  echo "- PR #67: \`$AUDIO_SHA\`"
  echo "- PR #68: \`$PRIVACY_SHA\`"
  echo "- Locally merged SHA: \`$MERGED_SHA\`"
  echo "- Python: \`$("$PYPATH" --version 2>&1)\`"
  echo "- Platform: macOS local temporary checkout"
  echo "- Overall: $([[ "$FAILURES" -eq 0 ]] && echo PASS || echo FAIL)"
  printf '%s\n' "${STATUS_LINES[@]}"
  echo
  echo "This report does not certify hosted CI, CodeQL, Windows/Linux builds,"
  echo "desktop signing/notarization, licensing, or physical vacuum models."
  echo "No local paths, credentials or private recordings are in this summary."
} >"$REPORT"
echo "--- Sanitized public report ---"
cat "$REPORT"
if gh issue comment 55 --repo "$REPO" --body-file "$REPORT"; then
  echo "Safe summary posted to issue #55 for remote review."
else
  echo "Failed to post summary; paste the sanitized report above into chat." >&2
fi
echo "Private test logs remain on your Mac: $LOGS"
if [[ "$FAILURES" -gt 0 ]]; then
  echo "$FAILURES checks failed. Nothing was merged or published." >&2
  exit 1
fi
echo "Mac-local QA complete. Windows/Linux and hosted gates remain independent."
