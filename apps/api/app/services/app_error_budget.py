"""App Error Budget — SLO-based error budget tracking for installed apps.

Tracks error budget consumption against Service Level Objectives:
- Configurable SLO target (e.g. 99.9% success rate)
- Rolling window budget computation (30-day default)
- Budget burn rate alerting
- Budget remaining / exhausted status
- Historical budget snapshots
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class BudgetStatus(str, Enum):
    HEALTHY = "healthy"       # >50% remaining
    WARNING = "warning"       # 10-50% remaining
    CRITICAL = "critical"     # <10% remaining
    EXHAUSTED = "exhausted"   # 0% remaining


@dataclass
class ErrorBudgetConfig:
    """SLO configuration for an app."""

    app_id: str
    slo_target_pct: float = 99.9      # e.g. 99.9%
    window_days: int = 30
    total_requests: int = 0
    failed_requests: int = 0


@dataclass
class BudgetSnapshot:
    """Point-in-time error budget state."""

    app_id: str
    slo_target_pct: float
    actual_success_pct: float
    budget_total_minutes: float    # allowed downtime in window
    budget_consumed_minutes: float
    budget_remaining_minutes: float
    budget_remaining_pct: float
    burn_rate: float               # >1 = burning faster than sustainable
    status: BudgetStatus
    window_days: int
    computed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class AppErrorBudget:
    """Track SLO-based error budgets."""

    def __init__(self):
        self._configs: dict[str, ErrorBudgetConfig] = {}

    def configure(self, app_id: str, slo_target_pct: float = 99.9,
                  window_days: int = 30) -> ErrorBudgetConfig:
        if not 0 < slo_target_pct < 100:
            raise ValueError("SLO target must be between 0 and 100 (exclusive)")
        config = ErrorBudgetConfig(app_id=app_id, slo_target_pct=slo_target_pct,
                                    window_days=window_days)
        self._configs[app_id] = config
        return config

    def record(self, app_id: str, total: int, failed: int) -> None:
        """Record request counts for the current window."""
        config = self._configs.get(app_id)
        if config is None:
            config = self.configure(app_id)
        if total < 0 or failed < 0:
            raise ValueError("Counts must be non-negative")
        if failed > total:
            raise ValueError("Failed cannot exceed total")
        config.total_requests = total
        config.failed_requests = failed

    def get_snapshot(self, app_id: str) -> BudgetSnapshot:
        """Compute the current error budget snapshot."""
        config = self._configs.get(app_id)
        if config is None:
            return BudgetSnapshot(
                app_id=app_id, slo_target_pct=99.9,
                actual_success_pct=100.0,
                budget_total_minutes=0, budget_consumed_minutes=0,
                budget_remaining_minutes=0, budget_remaining_pct=100.0,
                burn_rate=0, status=BudgetStatus.HEALTHY, window_days=30,
            )

        total = config.total_requests
        failed = config.failed_requests
        slo = config.slo_target_pct
        window = config.window_days

        if total == 0:
            return BudgetSnapshot(
                app_id=app_id, slo_target_pct=slo,
                actual_success_pct=100.0,
                budget_total_minutes=window * 24 * 60 * (1 - slo / 100),
                budget_consumed_minutes=0,
                budget_remaining_minutes=window * 24 * 60 * (1 - slo / 100),
                budget_remaining_pct=100.0,
                burn_rate=0, status=BudgetStatus.HEALTHY, window_days=window,
            )

        actual_success = ((total - failed) / total) * 100
        total_minutes = window * 24 * 60
        allowed_error_pct = 100 - slo
        budget_total = total_minutes * (allowed_error_pct / 100)
        actual_error_pct = (failed / total) * 100
        budget_consumed = total_minutes * (actual_error_pct / 100)
        budget_remaining = max(0, budget_total - budget_consumed)
        budget_remaining_pct = (budget_remaining / budget_total * 100) if budget_total > 0 else 0

        # Burn rate: >1 means burning faster than the SLO allows
        burn_rate = (actual_error_pct / allowed_error_pct) if allowed_error_pct > 0 else 0

        if budget_remaining_pct <= 0:
            status = BudgetStatus.EXHAUSTED
        elif budget_remaining_pct < 10:
            status = BudgetStatus.CRITICAL
        elif budget_remaining_pct < 50:
            status = BudgetStatus.WARNING
        else:
            status = BudgetStatus.HEALTHY

        return BudgetSnapshot(
            app_id=app_id, slo_target_pct=slo,
            actual_success_pct=round(actual_success, 4),
            budget_total_minutes=round(budget_total, 2),
            budget_consumed_minutes=round(budget_consumed, 2),
            budget_remaining_minutes=round(budget_remaining, 2),
            budget_remaining_pct=round(budget_remaining_pct, 2),
            burn_rate=round(burn_rate, 4),
            status=status, window_days=window,
        )

    def get_config(self, app_id: str) -> ErrorBudgetConfig | None:
        return self._configs.get(app_id)
