import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_token_revocation_log import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiTokenRevocationLog, RevocationEvent,
)

class TestTokenRevocationLog:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiTokenRevocationLog()
        svc.record("inst-1", RevocationEvent(event_id="e1", token_id="t1", consumer_id="c1", reason="manual", revoked_by="admin", timestamp=self._now()))
        summary = svc.get_summary("inst-1", "c1")
        assert summary.total_revocations == 1 and summary.by_reason["manual"] == 1

    def test_by_reason_breakdown(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiTokenRevocationLog()
        svc.record("inst-1", RevocationEvent(event_id="e1", token_id="t1", consumer_id="c1", reason="rotation", revoked_by="system", timestamp=self._now()))
        svc.record("inst-1", RevocationEvent(event_id="e2", token_id="t2", consumer_id="c1", reason="compromise", revoked_by="admin", timestamp=self._now()))
        svc.record("inst-1", RevocationEvent(event_id="e3", token_id="t3", consumer_id="c1", reason="rotation", revoked_by="system", timestamp=self._now()))
        summary = svc.get_summary("inst-1", "c1")
        assert summary.by_reason["rotation"] == 2 and summary.by_reason["compromise"] == 1

    def test_token_history(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiTokenRevocationLog()
        svc.record("inst-1", RevocationEvent(event_id="e1", token_id="t1", consumer_id="c1", reason="manual", revoked_by="admin", timestamp=self._now()))
        svc.record("inst-1", RevocationEvent(event_id="e2", token_id="t2", consumer_id="c1", reason="manual", revoked_by="admin", timestamp=self._now()))
        history = svc.get_token_history("inst-1", "c1", "t1")
        assert len(history) == 1

    def test_invalid_reason(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiTokenRevocationLog()
        with pytest.raises(ValueError, match="Invalid reason"):
            svc.record("inst-1", RevocationEvent(event_id="e1", token_id="t1", consumer_id="c1", reason="unknown", revoked_by="x"))

    def test_recent(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiTokenRevocationLog()
        svc.record("inst-1", RevocationEvent(event_id="e1", token_id="t1", consumer_id="c1", reason="manual", revoked_by="a", timestamp=self._now()))
        recent = svc.list_recent("inst-1", "c1")
        assert len(recent) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiTokenRevocationLog()
        svc.record("inst-1", RevocationEvent(event_id="e1", token_id="t1", consumer_id="c1", reason="manual", revoked_by="a", timestamp=self._now()))
        assert svc.get_summary("inst-2", "c1").total_revocations == 0
