import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_changelog import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiChangelog, ChangelogEntry,
)

class TestConsumerApiChangelog:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_publish_and_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiChangelog()
        svc.publish("inst-1", ChangelogEntry(entry_id="e1", version="2.0", title="New Auth", description="OAuth2 support", change_type="feature", published_at=self._now()))
        entries = svc.list_entries("inst-1")
        assert len(entries) == 1 and entries[0].title == "New Auth"

    def test_filter_by_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiChangelog()
        svc.publish("inst-1", ChangelogEntry(entry_id="e1", version="2.0", title="Feature", description="x", change_type="feature", published_at=self._now()))
        svc.publish("inst-1", ChangelogEntry(entry_id="e2", version="2.1", title="Fix", description="y", change_type="fix", published_at=self._now()))
        fixes = svc.list_entries("inst-1", change_type="fix")
        assert len(fixes) == 1 and fixes[0].title == "Fix"

    def test_unread_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiChangelog()
        svc.publish("inst-1", ChangelogEntry(entry_id="e1", version="1.0", title="A", description="x", published_at=self._now()))
        svc.publish("inst-1", ChangelogEntry(entry_id="e2", version="1.1", title="B", description="y", published_at=self._now()))
        assert svc.unread_count("inst-1", "c1") == 2
        svc.mark_read("inst-1", "c1", "e1", now=self._now())
        assert svc.unread_count("inst-1", "c1") == 1
        svc.mark_read("inst-1", "c1", "e2", now=self._now())
        assert svc.unread_count("inst-1", "c1") == 0

    def test_invalid_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiChangelog()
        with pytest.raises(ValueError, match="Invalid change_type"):
            svc.publish("inst-1", ChangelogEntry(entry_id="e1", version="1.0", title="X", description="x", change_type="unknown"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiChangelog()
        svc.publish("inst-1", ChangelogEntry(entry_id="e1", version="1.0", title="A", description="x", published_at=self._now()))
        assert len(svc.list_entries("inst-2")) == 0
