import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_request_budget import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestBudget

class TestRequestBudget:
    def test_allocate_and_consume(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestBudget()
        b = svc.allocate("inst-1", "c1", "2024-01", 1000)
        b = svc.consume("inst-1", "c1", "2024-01", 300)
        assert b.remaining == 700 and b.usage_pct == 30.0

    def test_exhausted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestBudget()
        svc.allocate("inst-1", "c1", "2024-01", 100)
        svc.consume("inst-1", "c1", "2024-01", 100)
        with pytest.raises(ValueError, match="exhausted"):
            svc.consume("inst-1", "c1", "2024-01", 1)

    def test_rollover(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestBudget()
        b = svc.allocate("inst-1", "c1", "2024-02", 1000, rollover=200)
        assert b.remaining == 1200

    def test_near_exhaustion(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestBudget()
        svc.allocate("inst-1", "c1", "2024-01", 100)
        svc.consume("inst-1", "c1", "2024-01", 95)
        near = svc.near_exhaustion("inst-1", 90.0)
        assert len(near) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestBudget()
        svc.allocate("inst-1", "c1", "2024-01", 1000)
        assert len(svc.list_budgets("inst-2")) == 0
