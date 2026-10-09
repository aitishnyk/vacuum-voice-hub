"""Prevent accidental version/path reuse during v2.0 source publishing."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v200_publisher_exact_release_contract():
    w = (ROOT / ".github/workflows/publish-stable-v200.yml").read_text("utf-8")
    assert "assert __version__ == '2.0.0'" in w
    assert "gh release create v2.0.0" in w
    assert "--notes-file docs/RELEASE_NOTES_V200.md" in w
    assert "release/VacuumVoiceHub-public-2.0.0.zip" in w
    assert "python scripts/v2_release_acceptance.py" in w
    assert "v1.9.0" not in w
    assert "V190" not in w
    assert (ROOT / "docs/RELEASE_NOTES_V200.md").is_file()
