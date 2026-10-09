"""Guard release workflow against stale references and versions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v170_exact_version_and_asset_contract():
    w = (ROOT / ".github/workflows/publish-stable-v170.yml").read_text("utf-8")
    assert "assert __version__ == '1.7.0'" in w
    assert "gh release create v1.7.0" in w
    assert "--notes-file docs/RELEASE_NOTES_V170.md" in w
    assert "release/VacuumVoiceHub-public-1.7.0.zip" in w
    assert "1.6.0" not in w
    assert "V160" not in w
    assert (ROOT / "docs/RELEASE_NOTES_V170.md").is_file()
