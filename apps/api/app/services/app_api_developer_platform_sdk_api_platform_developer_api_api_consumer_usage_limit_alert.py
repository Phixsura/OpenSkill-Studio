"""API Consumer Usage Limit Alert — alert consumers approaching usage limits."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class UsageLimitAlert:
    alert_id: str
    consumer_id: str
    metric: str  # "requests", "bandwidth", "webhooks", "storage"
    current_value: int
    limit_value: int
    threshold_pct: float  # when this was triggered (e.g. 80%)
    acknowledged: bool = False
    created_at: float = field(default_factory=time.time)

    @property
    def usage_pct(self) -> float:
        if self.limit_value == 0: return 0.0
        return round((self.current_value / self.limit_value) * 100, 1)

VALID_METRICS = {"requests", "bandwidth", "webhooks", "storage", "api_calls", "connections"}
THRESHOLDS = [50, 75, 90, 95, 100]

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerUsageLimitAlert:
    def __init__(self) -> None:
        self._alerts: dict[str, list[UsageLimitAlert]] = {}
        self._last_threshold: dict[tuple[str, str, str], float] = {}  # track last alerted threshold

    def check_and_alert(self, installation_id: str, consumer_id: str, metric: str, current: int, limit: int) -> UsageLimitAlert | None:
        if not installation_id: raise ValueError("installation_id is required")
        if metric not in VALID_METRICS: raise ValueError(f"Invalid metric: {metric}")
        if limit <= 0: return None
        pct = (current / limit) * 100
        key = (installation_id, consumer_id, metric)
        last = self._last_threshold.get(key, 0)
        for t in THRESHOLDS:
            if pct >= t > last:
                alert = UsageLimitAlert(alert_id=f"a-{consumer_id}-{metric}-{t}", consumer_id=consumer_id, metric=metric, current_value=current, limit_value=limit, threshold_pct=t)
                self._alerts.setdefault(installation_id, []).append(alert)
                self._last_threshold[key] = t
                return alert
        return None

    def acknowledge(self, installation_id: str, alert_id: str) -> UsageLimitAlert:
        for a in self._alerts.get(installation_id, []):
            if a.alert_id == alert_id:
                a.acknowledged = True
                return a
        raise KeyError(f"Alert {alert_id} not found")

    def unacknowledged(self, installation_id: str, consumer_id: str | None = None) -> list[UsageLimitAlert]:
        alerts = [a for a in self._alerts.get(installation_id, []) if not a.acknowledged]
        if consumer_id: alerts = [a for a in alerts if a.consumer_id == consumer_id]
        return alerts

    def alert_count(self, installation_id: str) -> int:
        return len(self._alerts.get(installation_id, []))
