"""Telemetry Dashboard — unified view of all extension telemetry signals.

The capstone telemetry service: aggregates metrics, traces, logs,
and events into a single dashboard with health scoring.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TelemetrySnapshot:
    extension_id: str
    # Metrics
    request_count: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    # Resources
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    # Traces
    active_traces: int = 0
    slow_traces: int = 0
    # Logs
    log_error_count: int = 0
    log_warn_count: int = 0
    # Health
    health_score: float = 100.0
    active_alerts: int = 0


class TelemetryDashboardService:
    """Unified telemetry dashboard aggregation."""

    def __init__(self):
        self._snapshots: dict[str, TelemetrySnapshot] = {}

    def update(self, extension_id: str, **kwargs) -> TelemetrySnapshot:
        if extension_id not in self._snapshots:
            self._snapshots[extension_id] = TelemetrySnapshot(extension_id=extension_id)
        snap = self._snapshots[extension_id]
        for k, v in kwargs.items():
            if hasattr(snap, k):
                setattr(snap, k, v)
        # Auto-calculate health score
        snap.health_score = self._calc_health(snap)
        return snap

    def _calc_health(self, s: TelemetrySnapshot) -> float:
        score = 100.0
        if s.request_count > 0:
            error_rate = s.error_count / s.request_count * 100
            if error_rate > 10: score -= 30
            elif error_rate > 5: score -= 15
            elif error_rate > 1: score -= 5
        if s.p99_latency_ms > 5000: score -= 20
        elif s.p99_latency_ms > 2000: score -= 10
        if s.cpu_percent > 90: score -= 15
        elif s.cpu_percent > 70: score -= 5
        if s.log_error_count > 50: score -= 10
        score -= s.active_alerts * 5
        return max(0, round(score, 1))

    def get_snapshot(self, extension_id: str) -> dict:
        s = self._snapshots.get(extension_id, TelemetrySnapshot(extension_id=extension_id))
        error_rate = round(s.error_count / max(s.request_count, 1) * 100, 2)
        return {
            "metrics": {"requests": s.request_count, "errors": s.error_count,
                        "error_rate": error_rate, "avg_latency": s.avg_latency_ms,
                        "p99_latency": s.p99_latency_ms},
            "resources": {"cpu": s.cpu_percent, "memory_mb": s.memory_mb},
            "signals": {"traces": s.active_traces, "slow_traces": s.slow_traces,
                        "log_errors": s.log_error_count, "log_warns": s.log_warn_count},
            "health": {"score": s.health_score, "alerts": s.active_alerts},
        }

    def get_all_health(self) -> list[dict]:
        return [{"extension_id": s.extension_id, "health": s.health_score,
                 "alerts": s.active_alerts}
                for s in sorted(self._snapshots.values(), key=lambda s: s.health_score)]
