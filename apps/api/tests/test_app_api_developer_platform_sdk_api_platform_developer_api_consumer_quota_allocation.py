import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_quota_allocation import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerQuotaAllocation

class TestConsumerQuotaAllocation:
    def test_allocate_and_consume(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerQuotaAllocation()
        q = svc.allocate("inst-1", "c1", "requests", 100)
        assert q.remaining == 100
        q = svc.consume("inst-1", "c1", "requests", 30)
        assert q.used == 30 and q.remaining == 70
        assert q.usage_pct == 30.0

    def test_exceed_quota(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerQuotaAllocation()
        svc.allocate("inst-1", "c1", "storage_mb", 10)
        with pytest.raises(ValueError, match="exceeded"):
            svc.consume("inst-1", "c1", "storage_mb", 11)

    def test_reset(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerQuotaAllocation()
        svc.allocate("inst-1", "c1", "webhooks", 50)
        svc.consume("inst-1", "c1", "webhooks", 50)
        assert svc.get_quota("inst-1", "c1", "webhooks").exhausted
        svc.reset("inst-1", "c1", "webhooks")
        assert svc.get_quota("inst-1", "c1", "webhooks").used == 0

    def test_near_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerQuotaAllocation()
        svc.allocate("inst-1", "c1", "requests", 100)
        svc.consume("inst-1", "c1", "requests", 85)
        near = svc.near_limit("inst-1", 80.0)
        assert len(near) == 1

    def test_bool_guard(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerQuotaAllocation()
        with pytest.raises(ValueError):
            svc.allocate("inst-1", "c1", "requests", True)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerQuotaAllocation()
        svc.allocate("inst-1", "c1", "requests", 100)
        assert len(svc.list_quotas("inst-2")) == 0
