"""API Consumer Anomaly Detector — detect unusual API usage patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class AnomalyAlert:
    alert_id: str
    consumer_id: str
    metric: str
    expected_value: float
    actual_value: float
    deviation_pct: float
    severity: str = "medium"  # "low", "medium", "high"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiAnomalyDetector:
    def __init__(self, threshold_pct: float = 50.0) -> None:
        self._baselines: dict[tuple[str, str, str], float] = {}
        self._alerts: dict[str, list[AnomalyAlert]] = {}
        self._threshold = max(10.0, threshold_pct)

    def set_baseline(self, installation_id: str, consumer_id: str, metric: str, value: float) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        if value < 0: raise ValueError("baseline must be non-negative")
        self._baselines[(installation_id, consumer_id, metric)] = value

    def check(self, installation_id: str, consumer_id: str, metric: str, actual: float) -> AnomalyAlert | None:
        key = (installation_id, consumer_id, metric)
        baseline = self._baselines.get(key)
        if baseline is None or baseline == 0: return None
        deviation = abs(actual - baseline) / baseline * 100
        if deviation < self._threshold: return None
        severity = "high" if deviation > 200 else "medium" if deviation > 100 else "low"
        alert = AnomalyAlert(alert_id=f"a-{consumer_id}-{metric}", consumer_id=consumer_id, metric=metric, expected_value=baseline, actual_value=actual, deviation_pct=round(deviation, 1), severity=severity)
        self._alerts.setdefault(installation_id, []).append(alert)
        return alert

    def recent_alerts(self, installation_id: str, limit: int = 20) -> list[AnomalyAlert]:
        return list(reversed(self._alerts.get(installation_id, [])[-limit:]))

    def alert_count(self, installation_id: str) -> int:
        return len(self._alerts.get(installation_id, []))
