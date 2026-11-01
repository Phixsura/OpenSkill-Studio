"""App API Developer Usage Quota Alert — alert when consumers approach quota limits."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class QuotaAlert:
    alert_id: str
    consumer_id: str
    resource: str
    threshold_pct: float
    current_usage_pct: float
    triggered: bool = False
    triggered_at: float | None = None
    notified: bool = False

class AppAPIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlert:
    def __init__(self) -> None:
        self._alerts: dict[tuple[str, str], QuotaAlert] = {}

    def configure(self, installation_id: str, alert_id: str, consumer_id: str, resource: str, threshold_pct: float) -> QuotaAlert:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 < threshold_pct <= 100: raise ValueError("threshold must be 0-100")
        key = (installation_id, alert_id)
        a = QuotaAlert(alert_id=alert_id, consumer_id=consumer_id, resource=resource, threshold_pct=threshold_pct, current_usage_pct=0.0)
        self._alerts[key] = a
        return a

    def evaluate(self, installation_id: str, alert_id: str, current_usage_pct: float) -> QuotaAlert:
        key = (installation_id, alert_id)
        a = self._alerts.get(key)
        if a is None: raise KeyError(f"Alert {alert_id} not found")
        a.current_usage_pct = current_usage_pct
        was_triggered = a.triggered
        a.triggered = current_usage_pct >= a.threshold_pct
        if a.triggered and not was_triggered:
            a.triggered_at = time.time()
            a.notified = False
        return a

    def triggered_alerts(self, installation_id: str) -> list[QuotaAlert]:
        return [a for (inst, _), a in self._alerts.items() if inst == installation_id and a.triggered]

    def by_consumer(self, installation_id: str, consumer_id: str) -> list[QuotaAlert]:
        return [a for (inst, _), a in self._alerts.items() if inst == installation_id and a.consumer_id == consumer_id]

    def all_alerts(self, installation_id: str) -> list[QuotaAlert]:
        return [a for (inst, _), a in self._alerts.items() if inst == installation_id]
