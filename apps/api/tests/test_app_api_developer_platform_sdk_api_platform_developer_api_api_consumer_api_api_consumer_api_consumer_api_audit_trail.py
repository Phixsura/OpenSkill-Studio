import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_audit_trail import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiAuditTrail, AuditEvent,
)

class TestConsumerApiAuditTrail:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiAuditTrail()
        svc.record("inst-1", AuditEvent(event_id="e1", consumer_id="c1", actor_id="u1", action="api_key.created", resource_type="api_key", resource_id="k1", timestamp=self._now()))
        events = svc.query("inst-1", "c1")
        assert len(events) == 1 and events[0].action == "api_key.created"

    def test_filter_by_action(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiAuditTrail()
        svc.record("inst-1", AuditEvent(event_id="e1", consumer_id="c1", actor_id="u1", action="api_key.created", resource_type="api_key", resource_id="k1", timestamp=self._now()))
        svc.record("inst-1", AuditEvent(event_id="e2", consumer_id="c1", actor_id="u1", action="webhook.updated", resource_type="webhook", resource_id="w1", timestamp=self._now()))
        events = svc.query("inst-1", "c1", action="webhook.updated")
        assert len(events) == 1

    def test_filter_by_actor(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiAuditTrail()
        svc.record("inst-1", AuditEvent(event_id="e1", consumer_id="c1", actor_id="u1", action="x", resource_type="t", resource_id="r", timestamp=self._now()))
        svc.record("inst-1", AuditEvent(event_id="e2", consumer_id="c1", actor_id="u2", action="y", resource_type="t", resource_id="r", timestamp=self._now()))
        events = svc.query("inst-1", "c1", actor_id="u2")
        assert len(events) == 1 and events[0].actor_id == "u2"

    def test_count_by_action(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiAuditTrail()
        svc.record("inst-1", AuditEvent(event_id="e1", consumer_id="c1", actor_id="u1", action="login", resource_type="session", resource_id="s1", timestamp=self._now()))
        svc.record("inst-1", AuditEvent(event_id="e2", consumer_id="c1", actor_id="u1", action="login", resource_type="session", resource_id="s2", timestamp=self._now()))
        counts = svc.count_by_action("inst-1", "c1")
        assert counts["login"] == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiAuditTrail()
        svc.record("inst-1", AuditEvent(event_id="e1", consumer_id="c1", actor_id="u1", action="x", resource_type="t", resource_id="r", timestamp=self._now()))
        assert len(svc.query("inst-2", "c1")) == 0
