"""Publisher must never publish a mismatched release asset or note."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v150_exact_source_release_contract():
    source = (ROOT / ".github/workflows/publish-stable-v150.yml").read_text("utf-8")
    assert "assert __version__ == '1.5.0'" in source
    assert "gh release create v1.5.0" in source
    assert "--notes-file docs/RELEASE_NOTES_V150.md" in source
    assert "release/VacuumVoiceHub-public-1.5.0.zip" in source
    assert "1.4.0" not in source and "V140" not in source
    assert (ROOT / "docs/RELEASE_NOTES_V150.md").is_file()
