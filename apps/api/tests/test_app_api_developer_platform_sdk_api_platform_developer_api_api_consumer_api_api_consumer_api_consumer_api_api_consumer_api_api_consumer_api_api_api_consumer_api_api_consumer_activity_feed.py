import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_api_consumer_activity_feed import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerActivityFeed, ActivityEvent,
)

class TestConsumerActivityFeed:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_publish_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerActivityFeed()
        svc.publish("inst-1", ActivityEvent(event_id="e1", consumer_id="c1", actor="admin", action="created", resource_type="api_key", resource_id="k1", timestamp=self._now()))
        feed = svc.get_feed("inst-1", "c1")
        assert len(feed) == 1 and feed[0].action == "created"

    def test_filter_by_resource(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerActivityFeed()
        svc.publish("inst-1", ActivityEvent(event_id="e1", consumer_id="c1", actor="a", action="created", resource_type="api_key", resource_id="k1", timestamp=self._now()))
        svc.publish("inst-1", ActivityEvent(event_id="e2", consumer_id="c1", actor="a", action="updated", resource_type="webhook", resource_id="w1", timestamp=self._now()))
        assert len(svc.get_feed("inst-1", "c1", resource_type="webhook")) == 1

    def test_count_by_action(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerActivityFeed()
        svc.publish("inst-1", ActivityEvent(event_id="e1", consumer_id="c1", actor="a", action="created", resource_type="x", resource_id="1", timestamp=self._now()))
        svc.publish("inst-1", ActivityEvent(event_id="e2", consumer_id="c1", actor="a", action="created", resource_type="y", resource_id="2", timestamp=self._now()))
        svc.publish("inst-1", ActivityEvent(event_id="e3", consumer_id="c1", actor="a", action="deleted", resource_type="x", resource_id="1", timestamp=self._now()))
        counts = svc.count_by_action("inst-1", "c1")
        assert counts["created"] == 2 and counts["deleted"] == 1

    def test_recent_actors(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerActivityFeed()
        svc.publish("inst-1", ActivityEvent(event_id="e1", consumer_id="c1", actor="alice", action="x", resource_type="t", resource_id="1", timestamp=self._now()))
        svc.publish("inst-1", ActivityEvent(event_id="e2", consumer_id="c1", actor="bob", action="y", resource_type="t", resource_id="2", timestamp=self._now()))
        actors = svc.get_recent_actors("inst-1", "c1")
        assert actors == ["bob", "alice"]

    def test_cap(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerActivityFeed(max_per_consumer=3)
        for i in range(5):
            svc.publish("inst-1", ActivityEvent(event_id=f"e{i}", consumer_id="c1", actor="a", action="x", resource_type="t", resource_id=str(i), timestamp=self._now()))
        assert len(svc.get_feed("inst-1", "c1", limit=100)) == 3

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerActivityFeed()
        svc.publish("inst-1", ActivityEvent(event_id="e1", consumer_id="c1", actor="a", action="x", resource_type="t", resource_id="1", timestamp=self._now()))
        assert len(svc.get_feed("inst-2", "c1")) == 0
