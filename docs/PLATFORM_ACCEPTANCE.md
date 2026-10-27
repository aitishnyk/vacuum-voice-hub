# Native platform acceptance

Run on each exact advertised OS/architecture. Keep source, desktop, signing,
hardware and download statuses distinct. A passing smoke below does not attest
that a human heard the native player. Never change that field without listening.

## Reproduce a native build

On macOS/Linux with Python 3.12, a C toolchain, make and pkg-config:

```sh
python -m pip install '.[desktop,review-signing]' pyinstaller
python scripts/fetch_codec_sources.py --output work/codec-source
sh scripts/build_codec.sh work/codec-source
export VVH_FFMPEG="$PWD/work/codec-source/runtime/bin/ffmpeg"
export VVH_CODEC_NOTICES="$PWD/work/codec-source/NOTICES"
python scripts/build_desktop.py
```

PASS: a platform-named ZIP and JSON manifest appear under dist, and the codec
license output contains no `--enable-nonfree`. The source archive and notices
must accompany published binary assets. The default macOS imageio-ffmpeg binary
examined during v2.1 preparation was **not redistributable**; do not bundle it.
The build script refuses it. Windows needs an independently verified native
codec/toolchain; this shell recipe does not certify Windows support.

## Clean native runtime check

On macOS, extract the ZIP into a new directory, leave your developer virtual
environment, and run from a different current directory:

```sh
unzip VacuumVoiceHub-2.1.0-Darwin-x86_64.zip -d native-check
cd /tmp
/path/to/native-check/VacuumVoiceHub.app/Contents/MacOS/VacuumVoiceHub \
  --smoke-test /tmp/vvh-native-smoke.json
cat /tmp/vvh-native-smoke.json
```

Use the real absolute path to the extracted app. PASS requires exit code 0,
`gui_loaded`, `demo_e2e` and `server_closed` all true. This exercises bundled
resources, codec, processing/export and native GUI loading without manually
installed Python. The smoke deliberately reports native audible playback false.
On Windows/Linux run the adjacent native executable with the same arguments.

Then open the extracted application normally. Select Try Demo, press Original
Play, process and play a new preview, build/download, close the app, reopen and
repeat. PASS means audible speech in both players, a valid downloaded archive,
unchanged originals and no application process left after closure. Record the
OS, architecture, artifact SHA, date and exact observations in the platform report.
Do not reuse another OS's observations.

## Verify an actually published download

```sh
python scripts/verify_download.py ACTUAL_RELEASE_ASSET_URL EXPECTED_SHA256 \
  --output download-verification.json
```

Use the asset URL and hash from the release manifest, never an invented future
URL. PASS: exit 0 and `download_verified: true`. Check signing independently:
macOS `codesign -dv --verbose=4 VacuumVoiceHub.app` and `spctl -a -vv VacuumVoiceHub.app`;
Windows `Get-AuthenticodeSignature .\VacuumVoiceHub.exe`. Ad-hoc signatures used
by PyInstaller are not Apple Developer signing or notarization.

Publish only platforms with completed evidence. An unsigned public beta can be
explicitly marked as such after its actual native and download gates pass.
