"""Dashboard Summary — aggregate all platform metrics for developer dashboard.

Pulls together installs, revenue, errors, health, ratings into a
single dashboard summary with trends and alerts.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TrendMetric:
    current: float
    previous: float
    label: str

    @property
    def change_percent(self) -> float:
        if self.previous == 0:
            return 100.0 if self.current > 0 else 0.0
        return round((self.current - self.previous) / self.previous * 100, 1)

    @property
    def trend(self) -> str:
        if self.change_percent > 0:
            return "up"
        elif self.change_percent < 0:
            return "down"
        return "flat"


@dataclass
class DashboardAlert:
    severity: str  # info, warning, critical
    message: str
    action: str = ""


class ExtensionDashboardSummaryService:
    """Aggregates platform metrics into a developer dashboard."""

    def generate(self, metrics: dict) -> dict:
        trends = []
        for key in ["installs", "revenue_cents", "api_calls", "active_users"]:
            if key in metrics and f"{key}_prev" in metrics:
                tm = TrendMetric(metrics[key], metrics[f"{key}_prev"], key)
                trends.append({
                    "metric": key, "current": tm.current,
                    "previous": tm.previous, "change": tm.change_percent,
                    "trend": tm.trend,
                })

        alerts = self._detect_alerts(metrics)

        return {
            "trends": trends,
            "alerts": alerts,
            "health_score": metrics.get("health_score", 100),
            "extensions_count": metrics.get("extensions_count", 0),
            "total_installs": metrics.get("installs", 0),
            "total_revenue": metrics.get("revenue_cents", 0),
            "error_rate": metrics.get("error_rate", 0),
            "avg_rating": metrics.get("avg_rating", 0),
        }

    def _detect_alerts(self, metrics: dict) -> list[dict]:
        alerts = []
        error_rate = metrics.get("error_rate", 0)
        if error_rate > 10:
            alerts.append({"severity": "critical", "message": f"High error rate: {error_rate}%",
                           "action": "Check error logs"})
        elif error_rate > 5:
            alerts.append({"severity": "warning", "message": f"Elevated error rate: {error_rate}%",
                           "action": "Monitor closely"})

        health = metrics.get("health_score", 100)
        if health < 80:
            alerts.append({"severity": "warning", "message": f"Health score: {health}%",
                           "action": "Review health probes"})

        rating = metrics.get("avg_rating", 5)
        if rating < 3.0:
            alerts.append({"severity": "warning", "message": f"Low rating: {rating}",
                           "action": "Review user feedback"})

        return alerts
