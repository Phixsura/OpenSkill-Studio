"""Tests for App API Latency Budget — percentiles, violations."""

import pytest

from app.services.app_api_latency_budget import AppAPILatencyBudget


class TestBudget:
    def test_set(self):
        l = AppAPILatencyBudget()
        b = l.set_budget("inst-1", "/api/users", 50, 200, 500)
        assert b.p50_target_ms == 50


class TestPercentiles:
    def test_percentiles(self):
        l = AppAPILatencyBudget()
        l.set_budget("inst-1", "/api/users", 50, 200, 500)
        for i in range(100):
            l.record("inst-1", "/api/users", float(i))
        b = l.get_budget("inst-1", "/api/users")
        assert b.p50 == 50.0
        assert b.p95 == 95.0
        assert b.p99 == 99.0


class TestViolations:
    def test_no_violation(self):
        l = AppAPILatencyBudget()
        l.set_budget("inst-1", "/api/users", 100, 300, 600)
        for i in range(100):
            l.record("inst-1", "/api/users", float(i))
        assert l.check_violations("inst-1") == []

    def test_p99_violation(self):
        l = AppAPILatencyBudget()
        l.set_budget("inst-1", "/api/users", 100, 200, 50)  # p99 target too low
        for i in range(100):
            l.record("inst-1", "/api/users", float(i))
        violations = l.check_violations("inst-1")
        assert len(violations) == 1
        assert "p99" in violations[0]["violations"]


class TestIsolation:
    def test_cross(self):
        l = AppAPILatencyBudget()
        l.set_budget("inst-1", "/api", 50, 200, 500)
        assert l.list_budgets("inst-2") == []
