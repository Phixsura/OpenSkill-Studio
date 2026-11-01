import pytest
from app.services.app_api_developer_api_api_developer_api_api_error_budget_policy import AppAPIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicy

class TestErrorBudgetPolicy:
    def test_create(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicy()
        pol = p.create("inst-1", "p1", "/api/users", 99.9, 30)
        assert pol.slo_pct == 99.9

    def test_budget_calculation(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicy()
        p.create("inst-1", "p1", "/api", 99.0, 30)
        for _ in range(100): p.record("inst-1", "p1", True)
        pol = p.all_policies("inst-1")[0]
        assert pol.allowed_failures == 1  # 1% of 100

    def test_exhausted(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicy()
        p.create("inst-1", "p1", "/api", 99.0, 30)
        for _ in range(99): p.record("inst-1", "p1", True)
        p.record("inst-1", "p1", False)
        assert p.should_freeze("inst-1", "p1") is True

    def test_burn_rate(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicy()
        p.create("inst-1", "p1", "/api", 99.0, 30)
        for _ in range(90): p.record("inst-1", "p1", True)
        for _ in range(10): p.record("inst-1", "p1", False)
        pol = p.all_policies("inst-1")[0]
        assert pol.burn_rate > 1.0  # over-burning

    def test_isolation(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicy()
        p.create("inst-1", "p1", "/api", 99.0, 30)
        assert len(p.all_policies("inst-2")) == 0
