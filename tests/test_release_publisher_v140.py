"""Prevent copied publisher workflow version and artifact path mistakes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v140_release_publisher_exact_contract():
    workflow = (ROOT / ".github/workflows/publish-stable-v140.yml").read_text("utf-8")
    assert "assert __version__ == '1.4.0'" in workflow
    assert "gh release create v1.4.0" in workflow
    assert "--notes-file docs/RELEASE_NOTES_V140.md" in workflow
    assert "release/VacuumVoiceHub-public-1.4.0.zip" in workflow
    assert "1.3.0" not in workflow
    assert "V130" not in workflow
    assert (ROOT / "docs/RELEASE_NOTES_V140.md").is_file()
