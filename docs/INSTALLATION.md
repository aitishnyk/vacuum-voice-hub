# Installation and desktop trust

The authoritative download list is [GitHub Releases](https://github.com/aitishnyk/vacuum-voice-hub/releases).
Use only assets actually present there. Source-tested does not mean desktop-tested.
The v2.1 preparation includes a native macOS Intel build; other operating systems
must complete their own native acceptance before being advertised as tested downloads.

## macOS

For a published desktop ZIP, compare `shasum -a 256 VacuumVoiceHub-*.zip`
against the accompanying SHA256SUMS, extract, and move VacuumVoiceHub.app
to Applications. Open it normally. A build without Apple Developer signing
and notarization is **unsigned developer software**. Gatekeeper may block it;
review the source and provenance before using macOS's documented Open Anyway
flow. No blanket security-disabling or quarantine-removal command is required.
Intel and Apple Silicon artifacts are different; do not assume a universal build.

Source installation: follow [Getting started](GETTING_STARTED.md), using Python 3.12.

## Windows x64

Only use a native Windows build after its acceptance report is published.
A portable ZIP contains VacuumVoiceHub.exe and its adjacent runtime files;
keep the directory intact. Verify with PowerShell:

```powershell
Get-FileHash .\VacuumVoiceHub-2.1.0-Windows-AMD64.zip -Algorithm SHA256
```

An unsigned build has no verified publisher certificate. Do not label it signed.
Source installation uses Python 3.12 and the commands in Getting started.

## Linux x86_64

A portable executable still needs system GUI libraries. On Debian/Ubuntu:

```sh
sudo apt-get install python3-venv python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1
```

For source installation, create a Python 3.12 environment with
`python3.12 -m venv --system-site-packages .venv`, then install as described in
Getting started. Distribution package names and Python ABI must match.
If a native artifact is published, verify `sha256sum VacuumVoiceHub-*.zip`,
extract the whole directory and run `./VacuumVoiceHub/VacuumVoiceHub`.
No Linux native acceptance is implied by these build instructions.

## Codecs, optional tools and data

Source installations can use the imageio-ffmpeg dependency fallback. Desktop
builds use the separately built, pinned LGPL codec and include its notices and
matching source bundle; the nonfree macOS dependency binary is never redistributed. The bundled eight WAV demo files do not need eSpeak or Piper.
Optional TTS requires locally installed engines and separately licensed models.
Do not redistribute models without checking their licenses.

Data defaults: macOS `~/Library/Application Support/VacuumVoiceHub`, Windows
`%LOCALAPPDATA%\VacuumVoiceHub`, Linux `~/.local/share/vacuum-voice-hub`.
`VVH_DATA_DIR` selects an alternative local data directory. Keep backups of
`creator/`; demo work lives under `demo/` and can be removed independently.
