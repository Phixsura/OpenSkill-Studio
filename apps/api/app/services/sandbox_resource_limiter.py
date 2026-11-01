"""Sandbox Resource Limiter — enforce CPU, memory, network, and time limits for sandboxed app executions.

Provides resource governance for the ADR-016 sandboxed runtime:
- Per-execution CPU time, wall-clock time, and memory limits
- Per-installation concurrent execution caps
- Network egress byte budgets
- File I/O limits (read/write byte caps)
- Execution budget tracking (daily/monthly quotas)
- Resource usage snapshots for billing and analytics
- Automatic kill recommendations when limits are exceeded
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class LimitViolation(str, Enum):
    CPU_TIME = "cpu_time"
    WALL_TIME = "wall_time"
    MEMORY = "memory"
    CONCURRENT = "concurrent"
    NETWORK_EGRESS = "network_egress"
    FILE_IO = "file_io"
    DAILY_BUDGET = "daily_budget"
    MONTHLY_BUDGET = "monthly_budget"


class ExecutionTier(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


# ── Tier limits ──────────────────────────────────────────

@dataclass(frozen=True)
class ResourceLimits:
    """Resource limits for a single sandbox execution."""

    max_cpu_seconds: float
    max_wall_seconds: float
    max_memory_mb: int
    max_concurrent: int
    max_network_egress_mb: float
    max_file_io_mb: float
    daily_execution_budget: int     # max executions per day
    monthly_execution_budget: int   # max executions per month


TIER_LIMITS: dict[ExecutionTier, ResourceLimits] = {
    ExecutionTier.BASIC: ResourceLimits(
        max_cpu_seconds=5.0,
        max_wall_seconds=30.0,
        max_memory_mb=128,
        max_concurrent=2,
        max_network_egress_mb=1.0,
        max_file_io_mb=10.0,
        daily_execution_budget=100,
        monthly_execution_budget=2_000,
    ),
    ExecutionTier.STANDARD: ResourceLimits(
        max_cpu_seconds=30.0,
        max_wall_seconds=120.0,
        max_memory_mb=512,
        max_concurrent=5,
        max_network_egress_mb=10.0,
        max_file_io_mb=50.0,
        daily_execution_budget=1_000,
        monthly_execution_budget=20_000,
    ),
    ExecutionTier.PREMIUM: ResourceLimits(
        max_cpu_seconds=120.0,
        max_wall_seconds=600.0,
        max_memory_mb=2048,
        max_concurrent=10,
        max_network_egress_mb=100.0,
        max_file_io_mb=500.0,
        daily_execution_budget=10_000,
        monthly_execution_budget=200_000,
    ),
}


@dataclass
class ResourceSnapshot:
    """Current resource usage for a running execution."""

    execution_id: str
    cpu_seconds: float = 0.0
    wall_seconds: float = 0.0
    memory_mb: float = 0.0
    network_egress_mb: float = 0.0
    file_io_mb: float = 0.0
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    violations: list[LimitViolation] = field(default_factory=list)


@dataclass
class LimitCheckResult:
    """Result of checking resource usage against limits."""

    allowed: bool
    violations: list[LimitViolation]
    details: dict[str, str]  # violation → human description
    should_kill: bool = False  # hard limit exceeded → terminate


@dataclass
class BudgetStatus:
    """Execution budget status for an installation."""

    installation_id: str
    tier: ExecutionTier
    daily_used: int
    daily_limit: int
    daily_remaining: int
    monthly_used: int
    monthly_limit: int
    monthly_remaining: int
    concurrent_active: int
    concurrent_limit: int


class SandboxResourceLimiter:
    """Enforce resource limits for sandboxed executions."""

    def __init__(self):
        # installation_id → tier
        self._tiers: dict[str, ExecutionTier] = {}
        # execution_id → ResourceSnapshot
        self._active: dict[str, ResourceSnapshot] = {}
        # execution_id → installation_id
        self._exec_to_install: dict[str, str] = {}
        # installation_id → set of active execution_ids
        self._install_execs: dict[str, set[str]] = {}
        # (installation_id, day_key) → count
        self._daily_counts: dict[tuple[str, str], int] = {}
        # (installation_id, month_key) → count
        self._monthly_counts: dict[tuple[str, str], int] = {}

    def set_tier(self, installation_id: str, tier: ExecutionTier) -> None:
        self._tiers[installation_id] = tier

    def get_limits(self, installation_id: str) -> ResourceLimits:
        tier = self._tiers.get(installation_id, ExecutionTier.BASIC)
        return TIER_LIMITS[tier]

    # ── Execution lifecycle ──────────────────────────────

    def can_start(self, installation_id: str) -> LimitCheckResult:
        """Check whether a new execution can start (concurrency + budget)."""
        limits = self.get_limits(installation_id)
        violations = []
        details: dict[str, str] = {}

        # Concurrent check
        active = self._install_execs.get(installation_id, set())
        if len(active) >= limits.max_concurrent:
            violations.append(LimitViolation.CONCURRENT)
            details["concurrent"] = (
                f"{len(active)}/{limits.max_concurrent} concurrent executions"
            )

        # Daily budget
        now = datetime.now(UTC)
        dk = now.strftime("%Y-%m-%d")
        daily = self._daily_counts.get((installation_id, dk), 0)
        if daily >= limits.daily_execution_budget:
            violations.append(LimitViolation.DAILY_BUDGET)
            details["daily_budget"] = (
                f"{daily}/{limits.daily_execution_budget} daily executions"
            )

        # Monthly budget
        mk = now.strftime("%Y-%m")
        monthly = self._monthly_counts.get((installation_id, mk), 0)
        if monthly >= limits.monthly_execution_budget:
            violations.append(LimitViolation.MONTHLY_BUDGET)
            details["monthly_budget"] = (
                f"{monthly}/{limits.monthly_execution_budget} monthly executions"
            )

        return LimitCheckResult(
            allowed=len(violations) == 0,
            violations=violations,
            details=details,
        )

    def start_execution(self, execution_id: str, installation_id: str) -> ResourceSnapshot:
        """Register a new execution. Caller should check can_start() first."""
        snapshot = ResourceSnapshot(execution_id=execution_id)
        self._active[execution_id] = snapshot
        self._exec_to_install[execution_id] = installation_id
        self._install_execs.setdefault(installation_id, set()).add(execution_id)

        # Increment budget counters
        now = datetime.now(UTC)
        dk = now.strftime("%Y-%m-%d")
        mk = now.strftime("%Y-%m")
        self._daily_counts[(installation_id, dk)] = (
            self._daily_counts.get((installation_id, dk), 0) + 1
        )
        self._monthly_counts[(installation_id, mk)] = (
            self._monthly_counts.get((installation_id, mk), 0) + 1
        )

        log.info(
            "sandbox.execution_started",
            execution_id=execution_id,
            installation_id=installation_id,
        )
        return snapshot

    def update_usage(self, execution_id: str, cpu_seconds: float = 0,
                     wall_seconds: float = 0, memory_mb: float = 0,
                     network_egress_mb: float = 0, file_io_mb: float = 0) -> LimitCheckResult:
        """Update resource usage and check against limits.

        Returns violations found. Caller should terminate if should_kill is True.
        """
        snapshot = self._active.get(execution_id)
        if snapshot is None:
            return LimitCheckResult(allowed=False, violations=[], details={"error": "Unknown execution"})

        snapshot.cpu_seconds = cpu_seconds
        snapshot.wall_seconds = wall_seconds
        snapshot.memory_mb = memory_mb
        snapshot.network_egress_mb = network_egress_mb
        snapshot.file_io_mb = file_io_mb

        installation_id = self._exec_to_install.get(execution_id, "")
        limits = self.get_limits(installation_id)

        violations = []
        details: dict[str, str] = {}
        should_kill = False

        if cpu_seconds > limits.max_cpu_seconds:
            violations.append(LimitViolation.CPU_TIME)
            details["cpu_time"] = f"{cpu_seconds:.1f}s > {limits.max_cpu_seconds}s"
            should_kill = True

        if wall_seconds > limits.max_wall_seconds:
            violations.append(LimitViolation.WALL_TIME)
            details["wall_time"] = f"{wall_seconds:.1f}s > {limits.max_wall_seconds}s"
            should_kill = True

        if memory_mb > limits.max_memory_mb:
            violations.append(LimitViolation.MEMORY)
            details["memory"] = f"{memory_mb:.0f}MB > {limits.max_memory_mb}MB"
            should_kill = True

        if network_egress_mb > limits.max_network_egress_mb:
            violations.append(LimitViolation.NETWORK_EGRESS)
            details["network_egress"] = f"{network_egress_mb:.1f}MB > {limits.max_network_egress_mb}MB"

        if file_io_mb > limits.max_file_io_mb:
            violations.append(LimitViolation.FILE_IO)
            details["file_io"] = f"{file_io_mb:.1f}MB > {limits.max_file_io_mb}MB"

        snapshot.violations = violations

        if violations:
            log.warning(
                "sandbox.limit_violation",
                execution_id=execution_id,
                violations=[v.value for v in violations],
                should_kill=should_kill,
            )

        return LimitCheckResult(
            allowed=len(violations) == 0,
            violations=violations,
            details=details,
            should_kill=should_kill,
        )

    def end_execution(self, execution_id: str) -> ResourceSnapshot | None:
        """Mark an execution as finished and release its resources."""
        snapshot = self._active.pop(execution_id, None)
        if snapshot is None:
            return None

        installation_id = self._exec_to_install.pop(execution_id, None)
        if installation_id and installation_id in self._install_execs:
            self._install_execs[installation_id].discard(execution_id)

        log.info(
            "sandbox.execution_ended",
            execution_id=execution_id,
            cpu_seconds=round(snapshot.cpu_seconds, 2),
            memory_peak_mb=round(snapshot.memory_mb, 1),
        )
        return snapshot

    # ── Status queries ───────────────────────────────────

    def get_budget_status(self, installation_id: str) -> BudgetStatus:
        """Get current budget status for an installation."""
        tier = self._tiers.get(installation_id, ExecutionTier.BASIC)
        limits = TIER_LIMITS[tier]
        now = datetime.now(UTC)

        dk = now.strftime("%Y-%m-%d")
        mk = now.strftime("%Y-%m")
        daily = self._daily_counts.get((installation_id, dk), 0)
        monthly = self._monthly_counts.get((installation_id, mk), 0)
        active = self._install_execs.get(installation_id, set())

        return BudgetStatus(
            installation_id=installation_id,
            tier=tier,
            daily_used=daily,
            daily_limit=limits.daily_execution_budget,
            daily_remaining=max(0, limits.daily_execution_budget - daily),
            monthly_used=monthly,
            monthly_limit=limits.monthly_execution_budget,
            monthly_remaining=max(0, limits.monthly_execution_budget - monthly),
            concurrent_active=len(active),
            concurrent_limit=limits.max_concurrent,
        )

    def active_count(self, installation_id: str) -> int:
        return len(self._install_execs.get(installation_id, set()))

    def get_snapshot(self, execution_id: str) -> ResourceSnapshot | None:
        return self._active.get(execution_id)
