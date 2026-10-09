"""Guard against copied publisher version, note and ZIP path regressions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v180_source_publisher_contract():
    w = (ROOT / ".github/workflows/publish-stable-v180.yml").read_text("utf-8")
    assert "assert __version__ == '1.8.0'" in w
    assert "gh release create v1.8.0" in w
    assert "--notes-file docs/RELEASE_NOTES_V180.md" in w
    assert "release/VacuumVoiceHub-public-1.8.0.zip" in w
    assert "1.7.0" not in w
    assert "V170" not in w
    assert (ROOT / "docs/RELEASE_NOTES_V180.md").is_file()
