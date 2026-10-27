# Try the offline demo

Open Home → Try Demo. No credentials, robot, account or network is required.
The eight prerecorded generic synthetic prompts are bundled as PCM WAVs,
with CC0 dedication, generation recipe and SHA-256 hashes in `demo_assets/`.

Select an event and press Play. Set −3, −6 or −9 dBFS and press Process preview.
The existing mastering engine trims silence, fades and normalizes into a new
file. Compare original and processed players and inspect the waveform.
Processing updates only the isolated demo's event assignment; later exports
use that assignment. It never changes the bundled or working original.

Build offline demo package creates a unique X10-format archive, reports its
SHA-256 and size and offers a download. Repeating processing or export creates
new outputs. The completion prompts are alternative recordings of one event,
not two hardware event IDs. This is a partial learning pack, never a full
replacement or an install action.

Continue in Creator Studio makes a new uniquely named Creator project from
original samples. The project is independent; your existing projects remain
untouched. In Creator, choose the actual target model and inspect QA/coverage.
To use your voice, create a new project and upload recordings you own.

Each Try Demo creates a fresh session. Removing only the `demo/` subdirectory
under the data directory allows a clean restart; never delete `creator/` to
reset a demo. Missing or corrupt bundled samples are integrity errors: reinstall
from a checksum-verified package. Failed decoding or disk writes leave originals
intact; retry with free disk space and a new session.
