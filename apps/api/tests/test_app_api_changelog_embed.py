import pytest
from app.services.app_api_changelog_embed import AppAPIChangelogEmbed

class TestEmbed:
    def test_configure(self):
        e = AppAPIChangelogEmbed()
        c = e.configure("inst-1", "dark", 10, False)
        assert c.theme == "dark"
        assert c.max_entries == 10

    def test_invalid_theme(self):
        e = AppAPIChangelogEmbed()
        with pytest.raises(ValueError):
            e.configure("inst-1", "neon")

    def test_default(self):
        e = AppAPIChangelogEmbed()
        c = e.get_config("inst-1")
        assert c.theme == "light"
