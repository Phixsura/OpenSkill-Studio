import pytest
from app.services.app_api_developer_api_api_developer_api_changelog_rss import AppAPIDeveloperAPIApiDeveloperApiChangelogRss

class TestChangelogRss:
    def test_publish(self):
        r = AppAPIDeveloperAPIApiDeveloperApiChangelogRss()
        item = r.publish("inst-1", "i1", "New endpoint", "Added /api/v2/users", "feature", "2.0")
        assert item.category == "feature"

    def test_invalid_category(self):
        r = AppAPIDeveloperAPIApiDeveloperApiChangelogRss()
        with pytest.raises(ValueError):
            r.publish("inst-1", "i1", "X", "Y", "unknown", "1.0")

    def test_feed(self):
        r = AppAPIDeveloperAPIApiDeveloperApiChangelogRss()
        r.publish("inst-1", "i1", "A", "desc", "feature", "1.0")
        r.publish("inst-1", "i2", "B", "desc", "fix", "1.1")
        feed = r.feed("inst-1")
        assert feed[0].item_id == "i2"  # newest first

    def test_by_version(self):
        r = AppAPIDeveloperAPIApiDeveloperApiChangelogRss()
        r.publish("inst-1", "i1", "A", "d", "feature", "1.0")
        r.publish("inst-1", "i2", "B", "d", "fix", "2.0")
        assert len(r.by_version("inst-1", "1.0")) == 1

    def test_render_xml(self):
        r = AppAPIDeveloperAPIApiDeveloperApiChangelogRss()
        r.publish("inst-1", "i1", "New Feature", "Added X", "feature", "1.0")
        xml = r.render_xml("inst-1")
        assert "<title>New Feature</title>" in xml
        assert "<?xml" in xml

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiDeveloperApiChangelogRss()
        r.publish("inst-1", "i1", "A", "d", "feature", "1.0")
        assert len(r.feed("inst-2")) == 0

    def test_xml_escape(self):
        r = AppAPIDeveloperAPIApiDeveloperApiChangelogRss()
        r.publish("inst-1", "i1", '<script>alert("xss")</script>', "A & B", "feature", "1.0")
        xml = r.render_xml("inst-1", "Test & Title")
        assert "<script>" not in xml
        assert "&lt;script&gt;" in xml
        assert "&amp;" in xml
