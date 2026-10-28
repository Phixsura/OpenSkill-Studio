"""Tests for App Error Budget — create, consume, exhaustion."""

import pytest

from app.services.app_error_budget import AppErrorBudget


class TestCreate:
    def test_create(self):
        e = AppErrorBudget()
        b = e.create("inst-1", "api", 99.9, 100000)
        assert b.budget_total == 99  # int(100000 * 0.001)
        assert b.budget_remaining == 99

    def test_invalid_slo(self):
        e = AppErrorBudget()
        with pytest.raises(ValueError, match="between 90"):
            e.create("inst-1", "api", 80.0, 1000)


class TestConsume:
    def test_record_errors(self):
        e = AppErrorBudget()
        e.create("inst-1", "api", 99.9, 100000)
        b = e.record_errors("inst-1", "api", 30)
        assert b.error_count == 30
        assert b.budget_remaining == 69
        assert b.budget_consumed_pct == 30.3

    def test_exhaust(self):
        e = AppErrorBudget()
        e.create("inst-1", "api", 99.9, 100000)
        e.record_errors("inst-1", "api", 99)
        b = e.get("inst-1", "api")
        assert b.is_exhausted is True
        assert b.budget_remaining == 0


class TestExhausted:
    def test_exhausted_services(self):
        e = AppErrorBudget()
        e.create("inst-1", "api", 99.9, 100000)
        e.create("inst-1", "db", 99.9, 100000)
        e.record_errors("inst-1", "api", 200)
        exhausted = e.exhausted_services("inst-1")
        assert len(exhausted) == 1
        assert exhausted[0].service_id == "api"


class TestReset:
    def test_reset(self):
        e = AppErrorBudget()
        e.create("inst-1", "api", 99.9, 100000)
        e.record_errors("inst-1", "api", 50)
        b = e.reset("inst-1", "api")
        assert b.error_count == 0
        assert b.budget_remaining == 99


class TestIsolation:
    def test_cross(self):
        e = AppErrorBudget()
        e.create("inst-1", "api", 99.9, 100000)
        assert e.list_budgets("inst-2") == []
