"""Fail before publishing if a copied release workflow uses stale assets."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v130_source_publisher_version_and_artifacts_match():
    workflow = (ROOT / ".github/workflows/publish-stable-v130.yml").read_text("utf-8")
    assert "assert __version__ == '1.3.0'" in workflow
    assert "gh release create v1.3.0" in workflow
    assert "--notes-file docs/RELEASE_NOTES_V130.md" in workflow
    assert "release/VacuumVoiceHub-public-1.3.0.zip" in workflow
    assert "v1.2.0" not in workflow
    assert "V120" not in workflow
    assert "public-1.2.0.zip" not in workflow
    assert (ROOT / "docs/RELEASE_NOTES_V130.md").is_file()
