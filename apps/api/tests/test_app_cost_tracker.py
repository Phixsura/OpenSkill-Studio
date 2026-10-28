"""Tests for App Cost Tracker — record, aggregate, budgets."""

import pytest

from app.services.app_cost_tracker import AppCostTracker


class TestRecord:
    def test_record(self):
        t = AppCostTracker()
        e = t.record("inst-1", "e1", "compute", 12.50, description="GPU hours")
        assert e.amount == 12.50

    def test_negative(self):
        t = AppCostTracker()
        with pytest.raises(ValueError, match="non-negative"):
            t.record("inst-1", "e1", "compute", -5)


class TestAggregate:
    def test_total(self):
        t = AppCostTracker()
        t.record("inst-1", "e1", "compute", 10.0)
        t.record("inst-1", "e2", "storage", 5.0)
        t.record("inst-1", "e3", "compute", 3.50)
        assert t.total("inst-1") == 18.50

    def test_total_by_category(self):
        t = AppCostTracker()
        t.record("inst-1", "e1", "compute", 10.0)
        t.record("inst-1", "e2", "storage", 5.0)
        assert t.total("inst-1", "compute") == 10.0

    def test_by_category(self):
        t = AppCostTracker()
        t.record("inst-1", "e1", "compute", 10.0)
        t.record("inst-1", "e2", "storage", 5.0)
        cats = t.by_category("inst-1")
        assert cats == {"compute": 10.0, "storage": 5.0}


class TestBudget:
    def test_set_budget(self):
        t = AppCostTracker()
        b = t.set_budget("inst-1", "compute", 100.0)
        assert b.monthly_limit == 100.0

    def test_alert(self):
        t = AppCostTracker()
        t.set_budget("inst-1", "compute", 100.0)
        t.record("inst-1", "e1", "compute", 85.0)
        alerts = t.budget_alerts("inst-1", threshold_pct=80.0)
        assert len(alerts) == 1
        assert alerts[0]["pct"] == 85.0

    def test_no_alert_under_threshold(self):
        t = AppCostTracker()
        t.set_budget("inst-1", "compute", 100.0)
        t.record("inst-1", "e1", "compute", 50.0)
        assert t.budget_alerts("inst-1") == []


class TestIsolation:
    def test_cross(self):
        t = AppCostTracker()
        t.record("inst-1", "e1", "compute", 10.0)
        assert t.total("inst-2") == 0
