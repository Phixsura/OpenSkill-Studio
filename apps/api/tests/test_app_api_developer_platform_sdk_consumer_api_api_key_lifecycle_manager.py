import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_key_lifecycle_manager import (
    AppAPIDeveloperPlatformSDKConsumerApiApiKeyLifecycleManager,
)

class TestApiKeyLifecycleManager:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_use(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiApiKeyLifecycleManager()
        raw, lc = svc.create_key("inst-1", "c1", label="Main Key", now=self._now())
        assert len(raw) > 20 and lc.status == "active"
        svc.use_key("inst-1", "c1", lc.key_id, self._now())
        assert lc.request_count == 1

    def test_expiry_check(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiApiKeyLifecycleManager()
        _, lc = svc.create_key("inst-1", "c1", ttl_days=30, now=self._now())
        svc.check_expiry("inst-1", "c1", lc.key_id, self._now() + timedelta(days=20))
        assert lc.status == "expiring_soon"
        svc.check_expiry("inst-1", "c1", lc.key_id, self._now() + timedelta(days=35))
        assert lc.status == "expired"

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiApiKeyLifecycleManager()
        _, lc = svc.create_key("inst-1", "c1", now=self._now())
        svc.revoke("inst-1", "c1", lc.key_id)
        assert lc.status == "revoked"
        with pytest.raises(ValueError, match="revoked"):
            svc.use_key("inst-1", "c1", lc.key_id, self._now())

    def test_list_by_status(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiApiKeyLifecycleManager()
        _, lc1 = svc.create_key("inst-1", "c1", now=self._now())
        _, lc2 = svc.create_key("inst-1", "c1", now=self._now())
        svc.revoke("inst-1", "c1", lc2.key_id)
        assert len(svc.list_keys("inst-1", "c1", status="active")) == 1

    def test_not_found(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiApiKeyLifecycleManager()
        with pytest.raises(ValueError, match="not found"):
            svc.use_key("inst-1", "c1", "missing", self._now())

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiApiKeyLifecycleManager()
        svc.create_key("inst-1", "c1", now=self._now())
        assert len(svc.list_keys("inst-2", "c1")) == 0
