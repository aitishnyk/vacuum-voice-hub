# Desktop application

Vacuum Voice Hub provides a native pywebview shell for the local UI and Creator Studio.

## Run

```bash
pip install "vacuum-voice-hub[desktop]"
vvh-desktop
```

## Multi-family target support

The packaged application can preview and calculate compatibility for all catalog model profiles.

Dreame numeric, IJAI ZIP and portable semantic builds use bundled Python/ffmpeg dependencies.

### Classic Roborock .pkg note

Encrypted legacy Roborock package creation currently requires the external `ccrypt` executable. The desktop binary does not pretend to bundle it.

On macOS with Homebrew:

```bash
brew install ccrypt
```

If `ccrypt` is absent, Roborock compatibility and preview still work; only encrypted `.pkg` creation/installation is unavailable.

## Signing

CI-built desktop binaries are build artifacts, not automatically code-signed or notarized. See [SIGNING.md](SIGNING.md).
