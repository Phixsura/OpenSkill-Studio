import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_api_changelog_aggregator import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiChangelogAggregator, ChangeEntry,
)

class TestChangelogAggregator:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_aggregate(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiChangelogAggregator()
        svc.add_entry("inst-1", ChangeEntry(entry_id="e1", version="2.0", change_type="added", title="OAuth2", published_at=self._now()))
        svc.add_entry("inst-1", ChangeEntry(entry_id="e2", version="2.0", change_type="fixed", title="Auth bug", published_at=self._now()))
        svc.add_entry("inst-1", ChangeEntry(entry_id="e3", version="2.1", change_type="deprecated", title="Old endpoint", breaking=True, published_at=self._now()))
        agg = svc.aggregate("inst-1")
        assert agg.total_entries == 3 and agg.breaking_count == 1 and len(agg.versions) == 2

    def test_by_version(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiChangelogAggregator()
        svc.add_entry("inst-1", ChangeEntry(entry_id="e1", version="1.0", change_type="added", title="A", published_at=self._now()))
        svc.add_entry("inst-1", ChangeEntry(entry_id="e2", version="2.0", change_type="added", title="B", published_at=self._now()))
        assert len(svc.get_by_version("inst-1", "1.0")) == 1

    def test_search(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiChangelogAggregator()
        svc.add_entry("inst-1", ChangeEntry(entry_id="e1", version="1.0", change_type="security", title="XSS fix", description="Fixed cross-site scripting", published_at=self._now()))
        assert len(svc.search("inst-1", "xss")) == 1

    def test_invalid_type(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiChangelogAggregator()
        with pytest.raises(ValueError, match="Invalid change_type"):
            svc.add_entry("inst-1", ChangeEntry(entry_id="e1", version="1.0", change_type="unknown", title="X"))

    def test_by_type_breakdown(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiChangelogAggregator()
        svc.add_entry("inst-1", ChangeEntry(entry_id="e1", version="1.0", change_type="added", title="A", published_at=self._now()))
        svc.add_entry("inst-1", ChangeEntry(entry_id="e2", version="1.0", change_type="added", title="B", published_at=self._now()))
        svc.add_entry("inst-1", ChangeEntry(entry_id="e3", version="1.0", change_type="fixed", title="C", published_at=self._now()))
        agg = svc.aggregate("inst-1")
        assert agg.by_type["added"] == 2 and agg.by_type["fixed"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiChangelogAggregator()
        svc.add_entry("inst-1", ChangeEntry(entry_id="e1", version="1.0", change_type="added", title="X", published_at=self._now()))
        assert svc.aggregate("inst-2").total_entries == 0
