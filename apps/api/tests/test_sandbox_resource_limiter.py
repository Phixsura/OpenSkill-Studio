"""Tests for Sandbox Resource Limiter — execution limits, budgets, concurrency."""

import pytest

from app.services.sandbox_resource_limiter import (
    BudgetStatus,
    ExecutionTier,
    LimitViolation,
    SandboxResourceLimiter,
    TIER_LIMITS,
)


class TestTierLimits:
    def test_basic_tier_defaults(self):
        limits = TIER_LIMITS[ExecutionTier.BASIC]
        assert limits.max_cpu_seconds == 5.0
        assert limits.max_wall_seconds == 30.0
        assert limits.max_memory_mb == 128
        assert limits.max_concurrent == 2

    def test_premium_tier_higher(self):
        basic = TIER_LIMITS[ExecutionTier.BASIC]
        premium = TIER_LIMITS[ExecutionTier.PREMIUM]
        assert premium.max_cpu_seconds > basic.max_cpu_seconds
        assert premium.max_memory_mb > basic.max_memory_mb
        assert premium.max_concurrent > basic.max_concurrent
        assert premium.daily_execution_budget > basic.daily_execution_budget


class TestCanStart:
    def test_allows_first_execution(self):
        limiter = SandboxResourceLimiter()
        result = limiter.can_start("inst-1")
        assert result.allowed is True
        assert result.violations == []

    def test_blocks_over_concurrent_limit(self):
        limiter = SandboxResourceLimiter()
        # Basic tier allows 2 concurrent
        limiter.start_execution("exec-1", "inst-1")
        limiter.start_execution("exec-2", "inst-1")
        result = limiter.can_start("inst-1")
        assert result.allowed is False
        assert LimitViolation.CONCURRENT in result.violations

    def test_allows_after_execution_ends(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        limiter.start_execution("exec-2", "inst-1")
        limiter.end_execution("exec-1")
        result = limiter.can_start("inst-1")
        assert result.allowed is True

    def test_different_installations_independent(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        limiter.start_execution("exec-2", "inst-1")
        # inst-2 should be fine
        result = limiter.can_start("inst-2")
        assert result.allowed is True


class TestStartExecution:
    def test_creates_snapshot(self):
        limiter = SandboxResourceLimiter()
        snap = limiter.start_execution("exec-1", "inst-1")
        assert snap.execution_id == "exec-1"
        assert snap.cpu_seconds == 0.0
        assert snap.memory_mb == 0.0

    def test_increments_budget_counters(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        limiter.start_execution("exec-2", "inst-1")
        status = limiter.get_budget_status("inst-1")
        assert status.daily_used == 2
        assert status.monthly_used == 2

    def test_tracks_active_count(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        assert limiter.active_count("inst-1") == 1
        limiter.start_execution("exec-2", "inst-1")
        assert limiter.active_count("inst-1") == 2


class TestUpdateUsage:
    def test_within_limits_ok(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        result = limiter.update_usage("exec-1", cpu_seconds=2.0, wall_seconds=10.0, memory_mb=64)
        assert result.allowed is True
        assert result.violations == []
        assert result.should_kill is False

    def test_cpu_exceeded_triggers_kill(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        # Basic tier: max 5s CPU
        result = limiter.update_usage("exec-1", cpu_seconds=6.0)
        assert result.allowed is False
        assert LimitViolation.CPU_TIME in result.violations
        assert result.should_kill is True

    def test_wall_time_exceeded_triggers_kill(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        # Basic tier: max 30s wall
        result = limiter.update_usage("exec-1", wall_seconds=35.0)
        assert result.should_kill is True
        assert LimitViolation.WALL_TIME in result.violations

    def test_memory_exceeded_triggers_kill(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        # Basic tier: max 128MB
        result = limiter.update_usage("exec-1", memory_mb=200)
        assert result.should_kill is True
        assert LimitViolation.MEMORY in result.violations

    def test_network_egress_exceeded_no_kill(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        # Basic: max 1MB egress
        result = limiter.update_usage("exec-1", network_egress_mb=2.0)
        assert LimitViolation.NETWORK_EGRESS in result.violations
        # Network isn't a hard kill trigger
        assert result.should_kill is False

    def test_file_io_exceeded(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        result = limiter.update_usage("exec-1", file_io_mb=15.0)
        assert LimitViolation.FILE_IO in result.violations

    def test_multiple_violations(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        result = limiter.update_usage(
            "exec-1", cpu_seconds=10, memory_mb=256, network_egress_mb=5
        )
        assert len(result.violations) == 3
        assert result.should_kill is True

    def test_unknown_execution(self):
        limiter = SandboxResourceLimiter()
        result = limiter.update_usage("nonexistent", cpu_seconds=1)
        assert result.allowed is False

    def test_premium_tier_higher_limits(self):
        limiter = SandboxResourceLimiter()
        limiter.set_tier("inst-1", ExecutionTier.PREMIUM)
        limiter.start_execution("exec-1", "inst-1")
        # 30s CPU would exceed basic (5s) but not premium (120s)
        result = limiter.update_usage("exec-1", cpu_seconds=30.0)
        assert result.allowed is True
        assert result.violations == []

    def test_snapshot_updated(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        limiter.update_usage("exec-1", cpu_seconds=2.5, memory_mb=80)
        snap = limiter.get_snapshot("exec-1")
        assert snap is not None
        assert snap.cpu_seconds == 2.5
        assert snap.memory_mb == 80


class TestEndExecution:
    def test_returns_final_snapshot(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        limiter.update_usage("exec-1", cpu_seconds=3.0, memory_mb=100)
        snap = limiter.end_execution("exec-1")
        assert snap is not None
        assert snap.cpu_seconds == 3.0

    def test_removes_from_active(self):
        limiter = SandboxResourceLimiter()
        limiter.start_execution("exec-1", "inst-1")
        limiter.end_execution("exec-1")
        assert limiter.active_count("inst-1") == 0
        assert limiter.get_snapshot("exec-1") is None

    def test_nonexistent_returns_none(self):
        limiter = SandboxResourceLimiter()
        assert limiter.end_execution("nonexistent") is None


class TestBudgetStatus:
    def test_fresh_installation_zeroes(self):
        limiter = SandboxResourceLimiter()
        status = limiter.get_budget_status("inst-1")
        assert status.daily_used == 0
        assert status.monthly_used == 0
        assert status.concurrent_active == 0
        assert status.daily_remaining == 100  # basic tier
        assert status.monthly_remaining == 2000

    def test_reflects_usage(self):
        limiter = SandboxResourceLimiter()
        for i in range(5):
            limiter.start_execution(f"exec-{i}", "inst-1")
            limiter.end_execution(f"exec-{i}")
        status = limiter.get_budget_status("inst-1")
        assert status.daily_used == 5
        assert status.daily_remaining == 95
        assert status.monthly_used == 5

    def test_blocks_when_daily_exhausted(self):
        limiter = SandboxResourceLimiter()
        for i in range(100):
            limiter.start_execution(f"exec-{i}", "inst-1")
            limiter.end_execution(f"exec-{i}")
        result = limiter.can_start("inst-1")
        assert result.allowed is False
        assert LimitViolation.DAILY_BUDGET in result.violations

    def test_tier_in_status(self):
        limiter = SandboxResourceLimiter()
        limiter.set_tier("inst-1", ExecutionTier.STANDARD)
        status = limiter.get_budget_status("inst-1")
        assert status.tier == ExecutionTier.STANDARD
        assert status.daily_limit == 1000
