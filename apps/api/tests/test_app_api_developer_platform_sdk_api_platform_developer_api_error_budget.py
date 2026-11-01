import pytest
import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_error_budget import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiErrorBudget

class TestErrorBudget:
    def test_budget_tracking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiErrorBudget()
        svc.create("inst-1", "/api/users", 99.9)
        b = svc.record_requests("inst-1", "/api/users", 10000, 5)
        # budget_total = 10000 * 0.001 = 10
        assert b.budget_total == pytest.approx(10.0)
        assert b.budget_remaining == pytest.approx(5.0)
        assert b.budget_consumed_pct == 50.0
        assert b.status == "warning"

    def test_exhausted_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiErrorBudget()
        svc.create("inst-1", "/api", 99.0)
        b = svc.record_requests("inst-1", "/api", 1000, 15)
        # budget_total = 1000 * 0.01 = 10, errors=15 > 10
        assert b.status == "exhausted"
        assert b.budget_consumed_pct >= 100

    def test_alerts(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiErrorBudget()
        svc.create("inst-1", "/a", 99.0)
        svc.record_requests("inst-1", "/a", 1000, 9)  # 90% consumed
        assert len(svc.alerts("inst-1", 80.0)) == 1

    def test_invalid_slo(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiErrorBudget()
        with pytest.raises(ValueError):
            svc.create("inst-1", "/api", 50.0)

    def test_errors_exceed_total(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiErrorBudget()
        svc.create("inst-1", "/api", 99.0)
        with pytest.raises(ValueError, match="exceed"):
            svc.record_requests("inst-1", "/api", 10, 20)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiErrorBudget()
        svc.create("inst-1", "/api", 99.9)
        assert len(svc.list_budgets("inst-2")) == 0
