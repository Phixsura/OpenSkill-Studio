"""Tests for Endpoint Performance Budget service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_perf_budget import (
    PerfBudgetTracker, PerfBudget, PerfSample,
)


class TestPerfBudgetTracker:
    def test_within_budget(self):
        svc = PerfBudgetTracker()
        svc.set_budget(PerfBudget("ep1", max_latency_p95_ms=200, max_latency_p99_ms=500))
        for i in range(20):
            svc.record(PerfSample("ep1", 50.0 + i))
        result = svc.check_budget("ep1")
        assert result["status"] == "within_budget"

    def test_over_budget_latency(self):
        svc = PerfBudgetTracker()
        svc.set_budget(PerfBudget("ep1", max_latency_p95_ms=100, max_latency_p99_ms=200))
        for i in range(20):
            svc.record(PerfSample("ep1", 150.0))
        result = svc.check_budget("ep1")
        assert result["status"] == "over_budget"
        assert any(v["metric"] == "latency_p95" for v in result["violations"])

    def test_over_budget_error_rate(self):
        svc = PerfBudgetTracker()
        svc.set_budget(PerfBudget("ep1", max_latency_p95_ms=500, max_latency_p99_ms=1000,
                                   max_error_rate_pct=5.0))
        for i in range(10):
            svc.record(PerfSample("ep1", 50.0, is_error=(i < 2)))
        result = svc.check_budget("ep1")
        assert result["status"] == "over_budget"

    def test_payload_budget(self):
        svc = PerfBudgetTracker()
        svc.set_budget(PerfBudget("ep1", max_latency_p95_ms=500, max_latency_p99_ms=1000,
                                   max_payload_bytes=1024))
        for i in range(5):
            svc.record(PerfSample("ep1", 50.0, payload_bytes=500))
        svc.record(PerfSample("ep1", 50.0, payload_bytes=2000))
        result = svc.check_budget("ep1")
        assert any(v["metric"] == "payload_size" for v in result["violations"])

    def test_no_budget(self):
        svc = PerfBudgetTracker()
        result = svc.check_budget("missing")
        assert result["status"] == "no_budget"

    def test_insufficient_data(self):
        svc = PerfBudgetTracker()
        svc.set_budget(PerfBudget("ep1", max_latency_p95_ms=100, max_latency_p99_ms=200))
        svc.record(PerfSample("ep1", 50.0))
        result = svc.check_budget("ep1")
        assert result["status"] == "insufficient_data"

    def test_get_all_budgets(self):
        svc = PerfBudgetTracker()
        svc.set_budget(PerfBudget("ep1", max_latency_p95_ms=200, max_latency_p99_ms=500))
        svc.set_budget(PerfBudget("ep2", max_latency_p95_ms=100, max_latency_p99_ms=300))
        for ep in ("ep1", "ep2"):
            for i in range(10):
                svc.record(PerfSample(ep, 50.0))
        results = svc.get_all_budgets()
        assert len(results) == 2

    def test_stats(self):
        svc = PerfBudgetTracker()
        svc.set_budget(PerfBudget("ep1", max_latency_p95_ms=200, max_latency_p99_ms=500))
        for i in range(10):
            svc.record(PerfSample("ep1", 50.0))
        stats = svc.get_stats()
        assert stats["total_budgets"] == 1
        assert stats["within_budget"] == 1

    def test_invalid_budget(self):
        svc = PerfBudgetTracker()
        with pytest.raises(ValueError):
            svc.set_budget(PerfBudget("ep1", max_latency_p95_ms=0, max_latency_p99_ms=100))

    def test_isolation(self):
        a, b = PerfBudgetTracker(), PerfBudgetTracker()
        a.set_budget(PerfBudget("ep1", max_latency_p95_ms=100, max_latency_p99_ms=200))
        assert b.check_budget("ep1")["status"] == "no_budget"
