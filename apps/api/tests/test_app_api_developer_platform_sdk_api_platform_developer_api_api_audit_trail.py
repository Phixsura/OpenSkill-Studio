import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_audit_trail import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAuditTrail, AuditEvent,
)

class TestApiAuditTrail:
    def test_record_and_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAuditTrail()
        svc.record("inst-1", AuditEvent(event_id="e1", actor_id="admin-1", actor_type="admin", action="key.create", resource_type="api_key", resource_id="k1"))
        events = svc.query("inst-1", actor_id="admin-1")
        assert len(events) == 1

    def test_filter_by_action(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAuditTrail()
        svc.record("inst-1", AuditEvent(event_id="e1", actor_id="a1", actor_type="admin", action="key.create", resource_type="api_key", resource_id="k1"))
        svc.record("inst-1", AuditEvent(event_id="e2", actor_id="a1", actor_type="admin", action="config.update", resource_type="config", resource_id="c1"))
        assert len(svc.query("inst-1", action="key.create")) == 1

    def test_security_events(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAuditTrail()
        svc.record("inst-1", AuditEvent(event_id="e1", actor_id="a1", actor_type="admin", action="key.revoke", resource_type="api_key", resource_id="k1"))
        svc.record("inst-1", AuditEvent(event_id="e2", actor_id="c1", actor_type="consumer", action="api.call", resource_type="endpoint", resource_id="/users"))
        sec = svc.recent_security_events("inst-1")
        assert len(sec) == 1

    def test_actions_by_actor(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAuditTrail()
        svc.record("inst-1", AuditEvent(event_id="e1", actor_id="a1", actor_type="admin", action="key.create", resource_type="k", resource_id="1"))
        svc.record("inst-1", AuditEvent(event_id="e2", actor_id="a1", actor_type="admin", action="key.create", resource_type="k", resource_id="2"))
        counts = svc.actions_by_actor("inst-1", "a1")
        assert counts["key.create"] == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAuditTrail()
        svc.record("inst-1", AuditEvent(event_id="e1", actor_id="a1", actor_type="system", action="config.update", resource_type="config", resource_id="c1"))
        assert svc.count("inst-2") == 0
