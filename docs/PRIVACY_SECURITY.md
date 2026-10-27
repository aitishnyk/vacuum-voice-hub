# Privacy and security

Studio recording import, decoding, mastering, QA, project backup and the bundled
demo run locally. The public website is a static catalog; it is not a remote
Creator Studio and does not receive your recordings. Downloading software,
obtaining optional TTS engines/models and following external documentation
links need a network connection.

Creator projects live in the platform data directory documented in
[Installation](INSTALLATION.md). Demo originals, processed previews and exports
are separate under `demo/`. They are not encrypted. Backups may contain private
audio and author metadata. Keep them private or encrypt with your own tools.

The local API binds to 127.0.0.1, validates Host and Origin and uses a random
session token for Creator and demo actions. There is no wildcard CORS.
Session tokens in media URLs remain local; do not publish URLs or raw logs.
Other local applications running as your user are outside this boundary.

Demo processing/export never invokes hardware transport. Actual robot actions
exist in the legacy local catalog/CLI and explicitly require device credentials
and model policy checks. Do not confuse building an offline package with
installing it. Physical evidence remains limited to the documented Xiaomi X10.

Report vulnerabilities through [SECURITY.md](../SECURITY.md). Original recordings
are preserved by non-destructive preview operations; no software substitutes
for keeping independent backups of valuable projects.
