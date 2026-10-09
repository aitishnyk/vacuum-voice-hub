"""Protect against stale-version paths in source publication workflows."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v160_release_workflow_contract():
    w = (ROOT / ".github/workflows/publish-stable-v160.yml").read_text("utf-8")
    assert "assert __version__ == '1.6.0'" in w
    assert "gh release create v1.6.0" in w
    assert "--notes-file docs/RELEASE_NOTES_V160.md" in w
    assert "release/VacuumVoiceHub-public-1.6.0.zip" in w
    assert "1.5.0" not in w and "V150" not in w
    assert (ROOT / "docs/RELEASE_NOTES_V160.md").is_file()
