import pytest
from app.services.app_api_developer_api_api_changelog_generator import AppAPIDeveloperAPIApiChangelogGenerator

class TestChangelogGenerator:
    def test_create_and_add(self):
        g = AppAPIDeveloperAPIApiChangelogGenerator()
        g.create("inst-1", "v2.0")
        e = g.add_entry("inst-1", "v2.0", "e1", "added", "New /api/users endpoint")
        assert e.category == "added"

    def test_invalid_category(self):
        g = AppAPIDeveloperAPIApiChangelogGenerator()
        g.create("inst-1", "v2.0")
        with pytest.raises(ValueError):
            g.add_entry("inst-1", "v2.0", "e1", "invalid", "test")

    def test_publish_locks(self):
        g = AppAPIDeveloperAPIApiChangelogGenerator()
        g.create("inst-1", "v2.0")
        g.publish("inst-1", "v2.0")
        with pytest.raises(ValueError, match="published"):
            g.add_entry("inst-1", "v2.0", "e1", "added", "test")

    def test_render_markdown(self):
        g = AppAPIDeveloperAPIApiChangelogGenerator()
        g.create("inst-1", "v2.0")
        g.add_entry("inst-1", "v2.0", "e1", "added", "New endpoint", breaking=True)
        g.add_entry("inst-1", "v2.0", "e2", "fixed", "Bug fix")
        md = g.render_markdown("inst-1", "v2.0")
        assert "## v2.0" in md
        assert "**BREAKING:**" in md
        assert "Bug fix" in md

    def test_isolation(self):
        g = AppAPIDeveloperAPIApiChangelogGenerator()
        g.create("inst-1", "v1.0")
        assert len(g.list_changelogs("inst-2")) == 0
