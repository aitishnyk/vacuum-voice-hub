from pathlib import Path
import re, shutil, subprocess, tempfile

root=Path(__file__).resolve().parents[1]
html=(root/"vacuum_voice_hub"/"web"/"index.html").read_text(encoding="utf-8")
blocks=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",html,flags=re.I|re.S)
if not blocks:
    raise SystemExit("No inline <script> block found")
node=shutil.which("node")
if not node:
    raise SystemExit("node is required for Web UI syntax gate")
with tempfile.TemporaryDirectory(prefix="vvh-js-") as td:
    for i,src in enumerate(blocks):
        p=Path(td)/f"inline-{i}.js"
        p.write_text(src,encoding="utf-8")
        r=subprocess.run([node,"--check",str(p)],text=True,capture_output=True)
        if r.returncode:
            raise SystemExit(r.stdout+r.stderr)
print(f"Web UI JavaScript syntax PASS ({len(blocks)} block(s))")
