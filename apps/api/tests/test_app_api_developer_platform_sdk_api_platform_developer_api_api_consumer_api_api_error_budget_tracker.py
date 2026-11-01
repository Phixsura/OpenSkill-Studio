import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_error_budget_tracker import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorBudgetTracker

class TestErrorBudgetTracker:
    def test_budget_consumption(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorBudgetTracker()
        svc.create("inst-1", "c1", slo_target_pct=99.0)
        b = svc.record("inst-1", "c1", 1000, 5)
        # budget_total = 1000 * 0.01 = 10, consumed = 5/10 = 50%
        assert b.budget_consumed == 50.0 and b.status == "warning"

    def test_exhausted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorBudgetTracker()
        svc.create("inst-1", "c1", slo_target_pct=99.0)
        svc.record("inst-1", "c1", 1000, 15)
        b = svc._budgets[("inst-1", "c1")]
        assert b.status == "exhausted"

    def test_at_risk(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorBudgetTracker()
        svc.create("inst-1", "c1", slo_target_pct=99.0)
        svc.record("inst-1", "c1", 1000, 9)  # 90% consumed
        assert len(svc.at_risk("inst-1", 80)) == 1

    def test_errors_exceed_requests(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorBudgetTracker()
        svc.create("inst-1", "c1")
        with pytest.raises(ValueError, match="exceed"):
            svc.record("inst-1", "c1", 10, 20)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorBudgetTracker()
        svc.create("inst-1", "c1")
        assert len(svc.list_budgets("inst-2")) == 0
