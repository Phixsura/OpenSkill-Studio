"""App Tenant Usage Summary — aggregate usage across all metrics per installation.

Provides a single-view summary of all usage:
- Combine API calls, storage, bandwidth, webhooks
- Overall health indicator
- Month-over-month comparison
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class MetricUsage:
    """Usage for a single metric."""

    metric: str
    current: float
    limit: float
    previous_period: float = 0.0

    @property
    def usage_pct(self) -> float:
        return round(self.current / self.limit * 100, 1) if self.limit > 0 else 0

    @property
    def growth_pct(self) -> float:
        if self.previous_period == 0:
            return 0
        return round((self.current - self.previous_period) / self.previous_period * 100, 1)


@dataclass
class TenantSummary:
    """Overall tenant usage summary."""

    installation_id: str
    metrics: list[MetricUsage]
    health: str  # "healthy", "warning", "critical"
    total_cost_cents: int = 0


class AppTenantUsageSummary:
    """Aggregate usage across all metrics."""

    def __init__(self) -> None:
        self._summaries: dict[str, TenantSummary] = {}

    def compute_summary(
        self,
        installation_id: str,
        metrics: list[dict],
        total_cost_cents: int = 0,
    ) -> TenantSummary:
        if not installation_id:
            raise ValueError("installation_id is required")

        metric_objs = [
            MetricUsage(
                metric=m["metric"], current=m["current"],
                limit=m["limit"], previous_period=m.get("previous_period", 0),
            )
            for m in metrics
        ]

        # Determine health
        max_usage = max((m.usage_pct for m in metric_objs), default=0)
        if max_usage >= 95:
            health = "critical"
        elif max_usage >= 80:
            health = "warning"
        else:
            health = "healthy"

        summary = TenantSummary(
            installation_id=installation_id,
            metrics=metric_objs, health=health,
            total_cost_cents=total_cost_cents,
        )
        self._summaries[installation_id] = summary
        return summary

    def get_summary(self, installation_id: str) -> TenantSummary:
        s = self._summaries.get(installation_id)
        if s is None:
            raise KeyError(f"No summary for {installation_id}")
        return s
