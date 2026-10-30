import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_session_manager import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSessionManager,
)

class TestConsumerApiSessionManager:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_create_and_validate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSessionManager()
        token, session = svc.create("inst-1", "c1", ip="1.2.3.4", now=self._now())
        found = svc.validate("inst-1", token, now=self._now())
        assert found is not None and found.session_id == session.session_id

    def test_expired(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSessionManager(session_ttl_hours=1)
        token, _ = svc.create("inst-1", "c1", now=self._now())
        assert svc.validate("inst-1", token, now=self._now() + timedelta(hours=2)) is None

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSessionManager()
        token, session = svc.create("inst-1", "c1", now=self._now())
        svc.revoke("inst-1", session.session_id)
        assert svc.validate("inst-1", token, now=self._now()) is None

    def test_revoke_all(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSessionManager()
        svc.create("inst-1", "c1", now=self._now())
        svc.create("inst-1", "c1", now=self._now())
        revoked = svc.revoke_all("inst-1", "c1")
        assert revoked == 2 and svc.active_count("inst-1", "c1") == 0

    def test_max_sessions_evicts_oldest(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSessionManager(max_sessions=2)
        t1, _ = svc.create("inst-1", "c1", now=self._now())
        svc.create("inst-1", "c1", now=self._now() + timedelta(minutes=1))
        svc.create("inst-1", "c1", now=self._now() + timedelta(minutes=2))
        assert svc.validate("inst-1", t1, now=self._now()) is None  # oldest evicted

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSessionManager()
        token, _ = svc.create("inst-1", "c1", now=self._now())
        assert svc.validate("inst-2", token, now=self._now()) is None
