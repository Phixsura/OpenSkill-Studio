import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_quota_manager import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestQuotaManager

class TestRequestQuotaManager:
    def test_set_and_consume(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestQuotaManager()
        svc.set_quota("inst-1", "c1", "hour", 1000)
        q = svc.consume("inst-1", "c1", "hour", 300)
        assert q.remaining == 700 and q.usage_pct == 30.0

    def test_exceed_quota(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestQuotaManager()
        svc.set_quota("inst-1", "c1", "minute", 10)
        svc.consume("inst-1", "c1", "minute", 10)
        with pytest.raises(ValueError, match="exceeded"):
            svc.consume("inst-1", "c1", "minute", 1)

    def test_rollover(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestQuotaManager()
        svc.set_quota("inst-1", "c1", "day", 100)
        svc.consume("inst-1", "c1", "day", 80)
        svc.reset("inst-1", "c1", "day", rollover_unused=True)
        q = svc._quotas[("inst-1", "c1", "day")]
        assert q.rollover_from_previous == 20 and q.total_available == 120

    def test_near_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestQuotaManager()
        svc.set_quota("inst-1", "c1", "hour", 100)
        svc.consume("inst-1", "c1", "hour", 85)
        assert len(svc.near_limit("inst-1", 80)) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestQuotaManager()
        svc.set_quota("inst-1", "c1", "hour", 100)
        assert len(svc.list_quotas("inst-2")) == 0
