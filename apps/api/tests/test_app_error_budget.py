"""Tests for App Error Budget — SLO config, budget computation, burn rate, status."""

import pytest

from app.services.app_error_budget import (
    AppErrorBudget,
    BudgetStatus,
)


class TestConfigure:
    def test_default_config(self):
        eb = AppErrorBudget()
        cfg = eb.configure("app-1")
        assert cfg.slo_target_pct == 99.9
        assert cfg.window_days == 30

    def test_custom_slo(self):
        eb = AppErrorBudget()
        cfg = eb.configure("app-1", slo_target_pct=99.5, window_days=7)
        assert cfg.slo_target_pct == 99.5
        assert cfg.window_days == 7

    def test_invalid_slo_rejected(self):
        eb = AppErrorBudget()
        with pytest.raises(ValueError):
            eb.configure("app-1", slo_target_pct=0)
        with pytest.raises(ValueError):
            eb.configure("app-1", slo_target_pct=100)


class TestRecord:
    def test_record_counts(self):
        eb = AppErrorBudget()
        eb.configure("app-1")
        eb.record("app-1", total=10000, failed=5)
        cfg = eb.get_config("app-1")
        assert cfg.total_requests == 10000
        assert cfg.failed_requests == 5

    def test_auto_configure_on_record(self):
        eb = AppErrorBudget()
        eb.record("app-new", total=100, failed=0)
        assert eb.get_config("app-new") is not None

    def test_negative_rejected(self):
        eb = AppErrorBudget()
        eb.configure("app-1")
        with pytest.raises(ValueError, match="non-negative"):
            eb.record("app-1", total=-1, failed=0)

    def test_failed_exceeds_total_rejected(self):
        eb = AppErrorBudget()
        eb.configure("app-1")
        with pytest.raises(ValueError, match="exceed"):
            eb.record("app-1", total=100, failed=101)


class TestSnapshot:
    def test_healthy_budget(self):
        eb = AppErrorBudget()
        eb.configure("app-1", slo_target_pct=99.9)
        eb.record("app-1", total=100000, failed=10)  # 99.99% success
        snap = eb.get_snapshot("app-1")
        assert snap.status == BudgetStatus.HEALTHY
        assert snap.budget_remaining_pct > 50
        assert snap.burn_rate < 1

    def test_exhausted_budget(self):
        eb = AppErrorBudget()
        eb.configure("app-1", slo_target_pct=99.9)
        eb.record("app-1", total=10000, failed=500)  # 95% success, way over
        snap = eb.get_snapshot("app-1")
        assert snap.status == BudgetStatus.EXHAUSTED
        assert snap.budget_remaining_pct == 0
        assert snap.burn_rate > 1

    def test_warning_budget(self):
        eb = AppErrorBudget()
        eb.configure("app-1", slo_target_pct=99.0)
        # 1% error budget, consume ~70% of it
        eb.record("app-1", total=10000, failed=70)  # 0.7% error rate
        snap = eb.get_snapshot("app-1")
        assert snap.status == BudgetStatus.WARNING

    def test_critical_budget(self):
        eb = AppErrorBudget()
        eb.configure("app-1", slo_target_pct=99.0)
        # consume ~95% of 1% budget
        eb.record("app-1", total=10000, failed=95)
        snap = eb.get_snapshot("app-1")
        assert snap.status == BudgetStatus.CRITICAL

    def test_zero_requests(self):
        eb = AppErrorBudget()
        eb.configure("app-1")
        eb.record("app-1", total=0, failed=0)
        snap = eb.get_snapshot("app-1")
        assert snap.actual_success_pct == 100.0
        assert snap.status == BudgetStatus.HEALTHY

    def test_unknown_app(self):
        eb = AppErrorBudget()
        snap = eb.get_snapshot("unknown")
        assert snap.status == BudgetStatus.HEALTHY
        assert snap.actual_success_pct == 100.0

    def test_perfect_success(self):
        eb = AppErrorBudget()
        eb.configure("app-1")
        eb.record("app-1", total=50000, failed=0)
        snap = eb.get_snapshot("app-1")
        assert snap.actual_success_pct == 100.0
        assert snap.budget_remaining_pct == 100.0
        assert snap.burn_rate == 0


class TestBurnRate:
    def test_burn_rate_under_one_is_safe(self):
        eb = AppErrorBudget()
        eb.configure("app-1", slo_target_pct=99.0)
        eb.record("app-1", total=10000, failed=5)  # 0.05% error vs 1% budget
        snap = eb.get_snapshot("app-1")
        assert snap.burn_rate < 1

    def test_burn_rate_over_one_is_danger(self):
        eb = AppErrorBudget()
        eb.configure("app-1", slo_target_pct=99.9)
        eb.record("app-1", total=10000, failed=20)  # 0.2% error vs 0.1% budget
        snap = eb.get_snapshot("app-1")
        assert snap.burn_rate > 1

    def test_burn_rate_exactly_one(self):
        eb = AppErrorBudget()
        eb.configure("app-1", slo_target_pct=99.0)
        eb.record("app-1", total=10000, failed=100)  # 1% error = 1% budget
        snap = eb.get_snapshot("app-1")
        assert snap.burn_rate == pytest.approx(1.0)
