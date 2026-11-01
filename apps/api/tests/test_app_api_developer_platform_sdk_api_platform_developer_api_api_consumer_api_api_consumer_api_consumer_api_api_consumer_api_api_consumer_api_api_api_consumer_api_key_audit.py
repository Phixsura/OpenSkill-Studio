import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_key_audit import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiKeyAudit, KeyAuditEvent,
)

class TestConsumerApiKeyAudit:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_history(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiKeyAudit()
        svc.record("inst-1", KeyAuditEvent(event_id="e1", key_id="k1", consumer_id="c1", action="created", actor_id="admin", timestamp=self._now()))
        history = svc.get_key_history("inst-1", "c1", "k1")
        assert len(history) == 1 and history[0].action == "created"

    def test_filter_by_action(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiKeyAudit()
        svc.record("inst-1", KeyAuditEvent(event_id="e1", key_id="k1", consumer_id="c1", action="created", actor_id="admin", timestamp=self._now()))
        svc.record("inst-1", KeyAuditEvent(event_id="e2", key_id="k1", consumer_id="c1", action="rotated", actor_id="admin", timestamp=self._now()))
        rotated = svc.get_consumer_history("inst-1", "c1", action="rotated")
        assert len(rotated) == 1

    def test_count_by_action(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiKeyAudit()
        svc.record("inst-1", KeyAuditEvent(event_id="e1", key_id="k1", consumer_id="c1", action="created", actor_id="a", timestamp=self._now()))
        svc.record("inst-1", KeyAuditEvent(event_id="e2", key_id="k2", consumer_id="c1", action="created", actor_id="a", timestamp=self._now()))
        svc.record("inst-1", KeyAuditEvent(event_id="e3", key_id="k1", consumer_id="c1", action="revoked", actor_id="a", timestamp=self._now()))
        counts = svc.count_by_action("inst-1", "c1")
        assert counts["created"] == 2 and counts["revoked"] == 1

    def test_invalid_action(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiKeyAudit()
        with pytest.raises(ValueError, match="Invalid action"):
            svc.record("inst-1", KeyAuditEvent(event_id="e1", key_id="k1", consumer_id="c1", action="hacked", actor_id="a"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiKeyAudit()
        svc.record("inst-1", KeyAuditEvent(event_id="e1", key_id="k1", consumer_id="c1", action="created", actor_id="a", timestamp=self._now()))
        assert len(svc.get_consumer_history("inst-2", "c1")) == 0
