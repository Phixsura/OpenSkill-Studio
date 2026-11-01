"""App API Developer API Usage Alert — threshold-based usage alerts."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class UsageAlert:
    alert_id: str
    metric: str  # "api_calls", "error_rate", "latency_p99", "webhook_failures"
    threshold: float
    operator: str  # "gt", "lt", "gte", "lte"
    current_value: float = 0.0
    triggered: bool = False
    triggered_at: float | None = None
    notification_sent: bool = False

class AppAPIDeveloperAPIApiDeveloperApiApiUsageAlert:
    def __init__(self) -> None:
        self._alerts: dict[tuple[str, str], UsageAlert] = {}

    def create(self, installation_id: str, alert_id: str, metric: str, threshold: float, operator: str) -> UsageAlert:
        if not installation_id: raise ValueError("installation_id is required")
        if metric not in ("api_calls", "error_rate", "latency_p99", "webhook_failures"): raise ValueError("invalid metric")
        if operator not in ("gt", "lt", "gte", "lte"): raise ValueError("invalid operator")
        key = (installation_id, alert_id)
        if key in self._alerts: raise ValueError(f"Alert {alert_id} exists")
        a = UsageAlert(alert_id=alert_id, metric=metric, threshold=threshold, operator=operator)
        self._alerts[key] = a
        return a

    def evaluate(self, installation_id: str, alert_id: str, current_value: float) -> UsageAlert:
        a = self._get(installation_id, alert_id)
        a.current_value = current_value
        ops = {"gt": current_value > a.threshold, "lt": current_value < a.threshold, "gte": current_value >= a.threshold, "lte": current_value <= a.threshold}
        was_triggered = a.triggered
        a.triggered = ops[a.operator]
        if a.triggered and not was_triggered:
            a.triggered_at = time.time()
            a.notification_sent = False
        return a

    def triggered_alerts(self, installation_id: str) -> list[UsageAlert]:
        return [a for (inst, _), a in self._alerts.items() if inst == installation_id and a.triggered]

    def all_alerts(self, installation_id: str) -> list[UsageAlert]:
        return [a for (inst, _), a in self._alerts.items() if inst == installation_id]

    def _get(self, installation_id: str, alert_id: str) -> UsageAlert:
        key = (installation_id, alert_id)
        a = self._alerts.get(key)
        if a is None: raise KeyError(f"Alert {alert_id} not found")
        return a
