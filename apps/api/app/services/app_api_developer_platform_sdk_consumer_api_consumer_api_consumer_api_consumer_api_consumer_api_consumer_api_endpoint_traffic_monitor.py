"""Consumer API Endpoint Traffic Monitor — real-time traffic monitoring per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class TrafficSnapshot:
    endpoint_path: str
    timestamp: datetime
    requests_per_second: float
    active_connections: int
    avg_latency_ms: float
    error_count: int

@dataclass
class TrafficAlert:
    endpoint_path: str
    alert_type: str  # "spike", "drop", "high_latency", "high_errors"
    message: str
    current_value: float
    threshold: float
    timestamp: datetime

@dataclass
class TrafficSummary:
    endpoint_path: str
    current_rps: float
    peak_rps: float
    avg_rps: float
    total_requests: int
    alerts: list[TrafficAlert] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointTrafficMonitor:
    def __init__(self) -> None:
        self._snapshots: dict[tuple[str, str], list[TrafficSnapshot]] = {}
        self._thresholds: dict[tuple[str, str], dict[str, float]] = {}

    def record_snapshot(self, installation_id: str, snapshot: TrafficSnapshot) -> TrafficSnapshot:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, snapshot.endpoint_path)
        if key not in self._snapshots:
            self._snapshots[key] = []
        self._snapshots[key].append(snapshot)
        if len(self._snapshots[key]) > 1000:
            self._snapshots[key] = self._snapshots[key][-1000:]
        return snapshot

    def set_thresholds(self, installation_id: str, endpoint_path: str, rps_spike: float = 100, latency_ms: float = 1000, error_pct: float = 5) -> None:
        self._thresholds[(installation_id, endpoint_path)] = {"rps_spike": rps_spike, "latency_ms": latency_ms, "error_pct": error_pct}

    def get_summary(self, installation_id: str, endpoint_path: str, now: datetime) -> TrafficSummary:
        snapshots = self._snapshots.get((installation_id, endpoint_path), [])
        if not snapshots:
            return TrafficSummary(endpoint_path=endpoint_path, current_rps=0, peak_rps=0, avg_rps=0, total_requests=0)
        current = snapshots[-1].requests_per_second
        peak = max(s.requests_per_second for s in snapshots)
        avg = sum(s.requests_per_second for s in snapshots) / len(snapshots)
        total = sum(int(s.requests_per_second) for s in snapshots)
        # Check alerts
        thresholds = self._thresholds.get((installation_id, endpoint_path), {"rps_spike": 100, "latency_ms": 1000, "error_pct": 5})
        alerts: list[TrafficAlert] = []
        if current > thresholds["rps_spike"]:
            alerts.append(TrafficAlert(endpoint_path=endpoint_path, alert_type="spike", message=f"RPS spike: {current}", current_value=current, threshold=thresholds["rps_spike"], timestamp=now))
        if snapshots[-1].avg_latency_ms > thresholds["latency_ms"]:
            alerts.append(TrafficAlert(endpoint_path=endpoint_path, alert_type="high_latency", message=f"High latency: {snapshots[-1].avg_latency_ms}ms", current_value=snapshots[-1].avg_latency_ms, threshold=thresholds["latency_ms"], timestamp=now))
        return TrafficSummary(endpoint_path=endpoint_path, current_rps=round(current, 1), peak_rps=round(peak, 1), avg_rps=round(avg, 1), total_requests=total, alerts=alerts)

    def list_endpoints(self, installation_id: str) -> list[str]:
        return sorted({ep for (inst, ep) in self._snapshots if inst == installation_id})
