import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_changelog_rss import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiChangelogRss, ChangelogItem,
)

class TestConsumerApiChangelogRss:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_add_and_feed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiChangelogRss()
        svc.add_item("inst-1", ChangelogItem(item_id="c1", title="New Auth", description="OAuth2", version="2.0", change_type="feature", published_at=self._now()))
        feed = svc.generate_feed("inst-1")
        assert len(feed.items) == 1 and feed.items[0].title == "New Auth"

    def test_render_xml(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiChangelogRss()
        svc.add_item("inst-1", ChangelogItem(item_id="c1", title="Fix <XSS>", description="Fixed & patched", version="1.1", change_type="fix", published_at=self._now()))
        xml = svc.render_xml("inst-1")
        assert "Fix &lt;XSS&gt;" in xml  # HTML escaped
        assert "Fixed &amp; patched" in xml

    def test_filter_by_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiChangelogRss()
        svc.add_item("inst-1", ChangelogItem(item_id="c1", title="A", description="x", version="1.0", change_type="feature", published_at=self._now()))
        svc.add_item("inst-1", ChangelogItem(item_id="c2", title="B", description="y", version="1.1", change_type="fix", published_at=self._now()))
        assert len(svc.list_items("inst-1", change_type="fix")) == 1

    def test_invalid_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiChangelogRss()
        with pytest.raises(ValueError, match="Invalid change_type"):
            svc.add_item("inst-1", ChangelogItem(item_id="c1", title="X", description="x", version="1.0", change_type="unknown", published_at=self._now()))

    def test_sorted_by_date(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiChangelogRss()
        from datetime import timedelta
        svc.add_item("inst-1", ChangelogItem(item_id="c1", title="Old", description="x", version="1.0", change_type="feature", published_at=self._now()))
        svc.add_item("inst-1", ChangelogItem(item_id="c2", title="New", description="y", version="2.0", change_type="feature", published_at=self._now() + timedelta(days=1)))
        feed = svc.generate_feed("inst-1")
        assert feed.items[0].title == "New"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiChangelogRss()
        svc.add_item("inst-1", ChangelogItem(item_id="c1", title="X", description="x", version="1.0", change_type="feature", published_at=self._now()))
        assert len(svc.list_items("inst-2")) == 0
