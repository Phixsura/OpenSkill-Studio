from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_retry_budget import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRetryBudget

class TestRetryBudget:
    def test_allow_within_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRetryBudget()
        svc.configure("inst-1", "c1", budget_per_minute=5)
        assert svc.try_retry("inst-1", "c1") is True
        b = svc.get_budget("inst-1", "c1")
        assert b.used_this_minute == 1

    def test_deny_over_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRetryBudget()
        svc.configure("inst-1", "c1", budget_per_minute=3)
        for _ in range(3): svc.try_retry("inst-1", "c1")
        assert svc.try_retry("inst-1", "c1") is False
        assert svc.get_budget("inst-1", "c1").total_exhausted == 1

    def test_reset(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRetryBudget()
        svc.configure("inst-1", "c1", budget_per_minute=5)
        svc.try_retry("inst-1", "c1")
        svc.reset_minute("inst-1", "c1")
        assert svc.get_budget("inst-1", "c1").used_this_minute == 0

    def test_no_budget_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRetryBudget()
        assert svc.try_retry("inst-1", "c1") is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRetryBudget()
        svc.configure("inst-1", "c1", 10)
        assert len(svc.list_budgets("inst-2")) == 0
