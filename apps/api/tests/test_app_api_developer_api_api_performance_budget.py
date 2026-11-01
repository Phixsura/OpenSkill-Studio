import pytest
from app.services.app_api_developer_api_api_performance_budget import AppAPIDeveloperAPIApiPerformanceBudget

class TestPerformanceBudget:
    def test_within_budget(self):
        b = AppAPIDeveloperAPIApiPerformanceBudget()
        b.set_budget("inst-1", "/api/users", 200.0, 50000)
        r = b.check("inst-1", "/api/users", 150, 30000)
        assert r.within_budget is True

    def test_latency_violation(self):
        b = AppAPIDeveloperAPIApiPerformanceBudget()
        b.set_budget("inst-1", "/api/users", 200.0, 50000)
        r = b.check("inst-1", "/api/users", 300, 30000)
        assert r.latency_ok is False
        assert r.within_budget is False

    def test_size_violation(self):
        b = AppAPIDeveloperAPIApiPerformanceBudget()
        b.set_budget("inst-1", "/api/users", 200.0, 50000)
        r = b.check("inst-1", "/api/users", 100, 100000)
        assert r.size_ok is False

    def test_violation_count(self):
        b = AppAPIDeveloperAPIApiPerformanceBudget()
        b.set_budget("inst-1", "/a", 100, 10000)
        b.check("inst-1", "/a", 50, 5000)
        b.check("inst-1", "/a", 200, 5000)
        assert b.all_budgets("inst-1")[0].violation_count == 1

    def test_isolation(self):
        b = AppAPIDeveloperAPIApiPerformanceBudget()
        b.set_budget("inst-1", "/a", 100, 10000)
        assert len(b.all_budgets("inst-2")) == 0
