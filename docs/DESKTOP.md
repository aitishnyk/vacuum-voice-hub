# Desktop application

Vacuum Voice Hub v0.5 includes a native desktop shell powered by pywebview.

## Run from Python

```bash
pip install "vacuum-voice-hub[desktop]"
vvh-desktop
```

or:

```bash
vvh desktop
```

The desktop process starts the same hardened HTTP application on an ephemeral `127.0.0.1` port and embeds it in a native application window. Creator Studio remains available from the desktop UI.

## Packaged builds

`.github/workflows/desktop.yml` builds one-file PyInstaller artifacts for:

- macOS
- Windows
- Linux

The packaging workflow runs for relevant pull requests, manual dispatches and version tags.

A successful source build does **not** mean a binary is code-signed or notarized. Signing/notarization remain separate release gates.

## Secrets

The optional `keyring` integration stores local MIIO tokens in the operating-system secret store:

```bash
pip install "vacuum-voice-hub[security]"
vvh credential save home-x10
vvh credential status home-x10
vvh install maxim-full --model dreame.vacuum.r2209 --ip 192.168.1.123 --credential home-x10
```

`vvh credential status` never prints the token.
