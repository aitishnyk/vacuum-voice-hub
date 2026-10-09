"""Reject accidental copied release notes, version and asset names."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v190_exact_publisher_version_contract():
    s = (ROOT / ".github/workflows/publish-stable-v190.yml").read_text("utf-8")
    assert "assert __version__ == '1.9.0'" in s
    assert "gh release create v1.9.0" in s
    assert "--notes-file docs/RELEASE_NOTES_V190.md" in s
    assert "release/VacuumVoiceHub-public-1.9.0.zip" in s
    assert "1.8.0" not in s
    assert "V180" not in s
    assert (ROOT / "docs/RELEASE_NOTES_V190.md").is_file()
