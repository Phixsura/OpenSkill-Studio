"""Tests for App API Performance Budget — set, record, violations."""

import pytest
from app.services.app_api_performance_budget import AppAPIPerformanceBudget


class TestBudget:
    def test_set(self):
        p = AppAPIPerformanceBudget()
        b = p.set_budget("inst-1", "b1", "response_time_ms", 200)
        assert b.within_budget is True

    def test_within(self):
        p = AppAPIPerformanceBudget()
        p.set_budget("inst-1", "b1", "response_time_ms", 200)
        b = p.record("inst-1", "b1", 150)
        assert b.within_budget is True
        assert b.usage_pct == 75.0

    def test_violation(self):
        p = AppAPIPerformanceBudget()
        p.set_budget("inst-1", "b1", "response_time_ms", 200)
        p.record("inst-1", "b1", 300)
        assert len(p.violations("inst-1")) == 1

    def test_violation_count(self):
        p = AppAPIPerformanceBudget()
        p.set_budget("inst-1", "b1", "payload_size_kb", 100)
        p.record("inst-1", "b1", 150)
        p.record("inst-1", "b1", 200)
        assert p.list_budgets("inst-1")[0].violations == 2


class TestIsolation:
    def test_cross(self):
        p = AppAPIPerformanceBudget()
        p.set_budget("inst-1", "b1", "x", 100)
        assert p.list_budgets("inst-2") == []
