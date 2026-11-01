import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_tenant_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiTenantConfig,
)

class TestConsumerApiTenantConfig:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiTenantConfig()
        svc.set("inst-1", "c1", "max_retries", 5, now=self._now())
        assert svc.get("inst-1", "c1", "max_retries") == 5

    def test_get_default(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiTenantConfig()
        assert svc.get("inst-1", "c1", "missing", default="fallback") == "fallback"

    def test_bool_value(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiTenantConfig()
        svc.set("inst-1", "c1", "debug", True, now=self._now())
        val = svc.get("inst-1", "c1", "debug")
        assert val is True and isinstance(val, bool)

    def test_delete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiTenantConfig()
        svc.set("inst-1", "c1", "temp", "x", now=self._now())
        svc.delete("inst-1", "c1", "temp")
        assert svc.get("inst-1", "c1", "temp") is None

    def test_versioning(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiTenantConfig()
        svc.set("inst-1", "c1", "a", "1", now=self._now())
        svc.set("inst-1", "c1", "b", "2", now=self._now())
        assert svc.get_version("inst-1", "c1") == 3  # initial 1 + 2 sets

    def test_history(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiTenantConfig()
        svc.set("inst-1", "c1", "x", "old", now=self._now())
        svc.set("inst-1", "c1", "x", "new", now=self._now())
        history = svc.get_history("inst-1", "c1")
        assert len(history) == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiTenantConfig()
        svc.set("inst-1", "c1", "key", "val", now=self._now())
        assert svc.get("inst-2", "c1", "key") is None
