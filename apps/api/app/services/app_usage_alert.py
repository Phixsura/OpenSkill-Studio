"""App Usage Alert — alert when usage approaches quota limits.

Monitors usage metrics against thresholds:
- Define alert thresholds per metric (warning, critical)
- Check current usage against thresholds
- Track alert acknowledgment
- Per-installation scoped alerts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class AlertLevel(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class UsageThreshold:
    """Threshold configuration for a metric."""

    metric: str
    warning_pct: float = 80.0   # % of limit
    critical_pct: float = 95.0  # % of limit
    limit: float = 0.0


@dataclass
class UsageAlertStatus:
    """Current alert status for a metric."""

    metric: str
    level: AlertLevel
    used: float
    limit: float
    usage_pct: float
    acknowledged: bool = False


class AppUsageAlert:
    """Alert when usage approaches quota limits."""

    def __init__(self) -> None:
        # (installation_id, metric) → UsageThreshold
        self._thresholds: dict[tuple[str, str], UsageThreshold] = {}
        # (installation_id, metric) → acknowledged
        self._acks: dict[tuple[str, str], bool] = {}

    def set_threshold(
        self,
        installation_id: str,
        metric: str,
        limit: float,
        warning_pct: float = 80.0,
        critical_pct: float = 95.0,
    ) -> UsageThreshold:
        """Set alert thresholds for a metric."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not metric:
            raise ValueError("metric is required")
        if limit <= 0:
            raise ValueError("limit must be positive")
        if not 0 < warning_pct < critical_pct <= 100:
            raise ValueError("thresholds must satisfy 0 < warning < critical <= 100")

        threshold = UsageThreshold(
            metric=metric, warning_pct=warning_pct,
            critical_pct=critical_pct, limit=limit,
        )
        self._thresholds[(installation_id, metric)] = threshold
        return threshold

    def check(
        self,
        installation_id: str,
        metric: str,
        used: float,
    ) -> UsageAlertStatus:
        """Check current usage against thresholds."""
        key = (installation_id, metric)
        threshold = self._thresholds.get(key)
        if threshold is None:
            raise KeyError(f"No threshold for metric {metric}")

        pct = (used / threshold.limit * 100) if threshold.limit > 0 else 0.0

        if pct >= threshold.critical_pct:
            level = AlertLevel.CRITICAL
        elif pct >= threshold.warning_pct:
            level = AlertLevel.WARNING
        else:
            level = AlertLevel.OK

        return UsageAlertStatus(
            metric=metric, level=level, used=used,
            limit=threshold.limit, usage_pct=round(pct, 1),
            acknowledged=self._acks.get(key, False),
        )

    def acknowledge(self, installation_id: str, metric: str) -> None:
        """Acknowledge an alert."""
        key = (installation_id, metric)
        if key not in self._thresholds:
            raise KeyError(f"No threshold for metric {metric}")
        self._acks[key] = True

    def reset_ack(self, installation_id: str, metric: str) -> None:
        """Reset acknowledgment (e.g., when usage drops back)."""
        self._acks.pop((installation_id, metric), None)

    def check_all(self, installation_id: str, usage: dict[str, float]) -> list[UsageAlertStatus]:
        """Check all configured metrics. Returns list of statuses."""
        results = []
        for (inst, metric), _ in self._thresholds.items():
            if inst != installation_id:
                continue
            if metric in usage:
                results.append(self.check(installation_id, metric, usage[metric]))
        return results

    def list_thresholds(self, installation_id: str) -> list[UsageThreshold]:
        return [t for (inst, _), t in self._thresholds.items() if inst == installation_id]
