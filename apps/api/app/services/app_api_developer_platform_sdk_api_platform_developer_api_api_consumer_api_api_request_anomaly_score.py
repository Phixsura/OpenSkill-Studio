"""API Consumer Request Anomaly Score — score individual requests for anomaly detection."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RequestAnomalyScore:
    request_id: str
    consumer_id: str
    anomaly_score: float  # 0.0 (normal) to 1.0 (highly anomalous)
    factors: dict[str, float]  # factor → contribution

    @property
    def is_anomalous(self) -> bool:
        return self.anomaly_score >= 0.7

    @property
    def severity(self) -> str:
        if self.anomaly_score >= 0.9: return "critical"
        if self.anomaly_score >= 0.7: return "high"
        if self.anomaly_score >= 0.4: return "medium"
        return "low"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAnomalyScore:
    def __init__(self) -> None:
        self._baselines: dict[tuple[str, str], dict[str, float]] = {}
        self._scores: dict[str, list[RequestAnomalyScore]] = {}

    def set_baseline(self, installation_id: str, consumer_id: str, avg_latency_ms: float, avg_body_bytes: int, typical_hour_start: int = 6, typical_hour_end: int = 22) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        self._baselines[(installation_id, consumer_id)] = {"avg_latency": avg_latency_ms, "avg_body": float(avg_body_bytes), "hour_start": float(typical_hour_start), "hour_end": float(typical_hour_end)}

    def score(self, installation_id: str, consumer_id: str, request_id: str, latency_ms: float, body_bytes: int, hour: int) -> RequestAnomalyScore:
        baseline = self._baselines.get((installation_id, consumer_id))
        if baseline is None:
            return RequestAnomalyScore(request_id=request_id, consumer_id=consumer_id, anomaly_score=0.0, factors={})
        factors: dict[str, float] = {}
        # Latency anomaly
        if baseline["avg_latency"] > 0:
            lat_ratio = latency_ms / baseline["avg_latency"]
            factors["latency"] = min(0.4, max(0, (lat_ratio - 1) * 0.2))
        # Body size anomaly
        if baseline["avg_body"] > 0:
            body_ratio = body_bytes / baseline["avg_body"]
            factors["body_size"] = min(0.3, max(0, (body_ratio - 1) * 0.15))
        # Off-hours
        if not (baseline["hour_start"] <= hour < baseline["hour_end"]):
            factors["off_hours"] = 0.3
        total = round(min(1.0, sum(factors.values())), 2)
        result = RequestAnomalyScore(request_id=request_id, consumer_id=consumer_id, anomaly_score=total, factors=factors)
        self._scores.setdefault(installation_id, []).append(result)
        return result

    def recent_anomalies(self, installation_id: str, limit: int = 20) -> list[RequestAnomalyScore]:
        return [s for s in self._scores.get(installation_id, []) if s.is_anomalous][-limit:]

    def anomaly_count(self, installation_id: str) -> int:
        return sum(1 for s in self._scores.get(installation_id, []) if s.is_anomalous)
