# Getting started

Vacuum Voice Hub is a local voice studio for robot vacuums. You can explore
and export audio without a robot, credentials or a cloud account.

## Install from source

Use Python 3.12. From a checked-out release:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install '.[desktop,review-signing]'
vvh desktop
```

Windows PowerShell: create the environment with `py -3.12 -m venv .venv`,
then run `.venv\Scripts\python -m pip install ".[desktop,review-signing]"`
and `.venv\Scripts\vvh desktop`. Linux needs GTK/WebKit (see [Installation](INSTALLATION.md)).
A Python source ZIP is not a standalone installer.

## First audio in a minute

1. Open Home and select **Try Demo**.
2. Select a robot event, then press Play under **Original recording**.
3. Choose a target peak and select **Process preview**.
4. Inspect the waveform and play the processed recording.
5. Select **Build offline demo package**, then **Download demo package**.
6. Select **Continue in Creator Studio** to create an independent project.

The eight bundled synthetic samples work offline. TTS is optional. Original
samples, processed previews and exports are separate. The two completion
phrases are alternatives for the same `clean.complete` semantic, so a copied
project has seven event assignments. Export is a partial learning pack for
Xiaomi X10, not a complete replacement pack or an installation.

## Your first project

In Creator Studio, expand **Create a new voice pack**. Use a unique ID,
name, author, language and a license you actually have permission to use.
Import recordings against semantic events, choose a target model and run
Validate, Coverage, Preflight and Audio QA before building. Use the recording
review checklist for listening and rights review. See [Creator guide](CREATOR_STUDIO.md),
[Demo tutorial](DEMO_TUTORIAL.md), and [Compatibility](COMPATIBILITY_GUIDE.md).

Projects are local. Existing Creator formats and model aliases remain valid.
Back up valuable projects before upgrading; see [Recovery](CREATOR_RECOVERY_V190.md).
