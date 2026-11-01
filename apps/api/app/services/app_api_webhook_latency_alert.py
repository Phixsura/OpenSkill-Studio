"""App API Webhook Latency Alert — alert on slow webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class LatencyAlert:
    alert_id: str
    destination: str
    threshold_ms: float
    current_avg_ms: float = 0.0
    triggered: bool = False
    trigger_count: int = 0

class AppAPIWebhookLatencyAlert:
    def __init__(self) -> None:
        self._alerts: dict[tuple[str, str], LatencyAlert] = {}

    def set_alert(self, installation_id: str, alert_id: str, destination: str, threshold_ms: float) -> LatencyAlert:
        if not installation_id: raise ValueError("installation_id is required")
        if threshold_ms <= 0: raise ValueError("threshold must be positive")
        a = LatencyAlert(alert_id=alert_id, destination=destination, threshold_ms=threshold_ms)
        self._alerts[(installation_id, alert_id)] = a
        return a

    def evaluate(self, installation_id: str, alert_id: str, avg_latency_ms: float) -> LatencyAlert:
        a = self._get(installation_id, alert_id)
        a.current_avg_ms = avg_latency_ms
        was_triggered = a.triggered
        a.triggered = avg_latency_ms > a.threshold_ms
        if a.triggered and not was_triggered:
            a.trigger_count += 1
        return a

    def triggered_alerts(self, installation_id: str) -> list[LatencyAlert]:
        return [a for (inst, _), a in self._alerts.items() if inst == installation_id and a.triggered]

    def list_alerts(self, installation_id: str) -> list[LatencyAlert]:
        return [a for (inst, _), a in self._alerts.items() if inst == installation_id]

    def _get(self, installation_id: str, alert_id: str) -> LatencyAlert:
        a = self._alerts.get((installation_id, alert_id))
        if a is None: raise KeyError(f"Alert {alert_id} not found")
        return a
