from pathlib import Path
import re,shutil,subprocess,tempfile

root=Path(__file__).resolve().parents[1]
html_files=sorted((root/"vacuum_voice_hub"/"web").glob("*.html"))
if not html_files:
    raise SystemExit("No Web UI HTML files found")
node=shutil.which("node")
if not node:
    raise SystemExit("node is required for Web UI syntax gate")
count=0
with tempfile.TemporaryDirectory(prefix="vvh-js-") as td:
    for html_file in html_files:
        html=html_file.read_text(encoding="utf-8")
        blocks=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",html,flags=re.I|re.S)
        if not blocks:
            raise SystemExit(f"No inline <script> block found in {html_file.name}")
        for i,src in enumerate(blocks):
            p=Path(td)/f"{html_file.stem}-{i}.js"
            p.write_text(src,encoding="utf-8")
            r=subprocess.run([node,"--check",str(p)],text=True,capture_output=True)
            if r.returncode:
                raise SystemExit(f"{html_file.name}:\n"+r.stdout+r.stderr)
            count+=1
print(f"Web UI JavaScript syntax PASS ({count} block(s) across {len(html_files)} file(s))")
