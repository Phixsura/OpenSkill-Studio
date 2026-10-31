"""App API Developer API Anomaly Detector — detect traffic and error anomalies."""
from __future__ import annotations
from dataclasses import dataclass, field
import statistics
import structlog

log = structlog.get_logger()

@dataclass
class Anomaly:
    anomaly_id: str
    endpoint: str
    metric: str  # "traffic", "error_rate", "latency"
    severity: str  # "warning", "critical"
    current_value: float
    baseline_value: float
    deviation_pct: float

class AppAPIDeveloperAPIApiAnomalyDetector:
    def __init__(self, warning_threshold: float = 2.0, critical_threshold: float = 3.0) -> None:
        self._warning = warning_threshold
        self._critical = critical_threshold
        self._baselines: dict[tuple[str, str, str], list[float]] = {}
        self._anomalies: dict[str, list[Anomaly]] = {}
        self._counter = 0

    def add_sample(self, installation_id: str, endpoint: str, metric: str, value: float) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, endpoint, metric)
        self._baselines.setdefault(key, []).append(value)

    def detect(self, installation_id: str, endpoint: str, metric: str, current_value: float) -> Anomaly | None:
        key = (installation_id, endpoint, metric)
        samples = self._baselines.get(key, [])
        if len(samples) < 5: return None
        mean = statistics.mean(samples)
        stdev = statistics.stdev(samples)
        if stdev == 0: return None
        z_score = abs(current_value - mean) / stdev
        if z_score < self._warning: return None
        severity = "critical" if z_score >= self._critical else "warning"
        deviation_pct = round((current_value - mean) / mean * 100, 1) if mean != 0 else 0.0
        self._counter += 1
        a = Anomaly(anomaly_id=f"anom-{self._counter}", endpoint=endpoint, metric=metric, severity=severity, current_value=current_value, baseline_value=round(mean, 2), deviation_pct=deviation_pct)
        self._anomalies.setdefault(installation_id, []).append(a)
        return a

    def recent_anomalies(self, installation_id: str, limit: int = 20) -> list[Anomaly]:
        return list(reversed(self._anomalies.get(installation_id, [])[-limit:]))

    def critical_count(self, installation_id: str) -> int:
        return sum(1 for a in self._anomalies.get(installation_id, []) if a.severity == "critical")
