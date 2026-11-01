import pytest
from app.services.app_api_developer_api_error_budget_tracker import AppAPIDeveloperAPIErrorBudgetTracker

class TestErrorBudgetTracker:
    def test_create_and_record(self):
        t = AppAPIDeveloperAPIErrorBudgetTracker()
        t.create("inst-1", "/api/users", 99.9)
        for _ in range(990): t.record("inst-1", "/api/users", True)
        for _ in range(10): t.record("inst-1", "/api/users", False)
        b = t.get("inst-1", "/api/users")
        assert b.current_success_pct == 99.0
        assert b.budget_exhausted is True

    def test_budget_remaining(self):
        t = AppAPIDeveloperAPIErrorBudgetTracker()
        t.create("inst-1", "/api/data", 99.0)
        for _ in range(100): t.record("inst-1", "/api/data", True)
        b = t.get("inst-1", "/api/data")
        assert b.budget_remaining_pct == 1.0

    def test_exhausted_list(self):
        t = AppAPIDeveloperAPIErrorBudgetTracker()
        t.create("inst-1", "/a", 99.0)
        t.create("inst-1", "/b", 99.0)
        for _ in range(50): t.record("inst-1", "/a", True)
        for _ in range(50): t.record("inst-1", "/a", False)
        assert len(t.exhausted("inst-1")) == 1

    def test_isolation(self):
        t = AppAPIDeveloperAPIErrorBudgetTracker()
        t.create("inst-1", "/a", 99.0)
        assert len(t.exhausted("inst-2")) == 0
