"""Sandbox Metrics Collector — collect and aggregate sandbox runtime metrics.

Gathers CPU, memory, network, disk, and custom metrics from sandboxes
with time-series bucketing, percentile calculation, and alerting.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class MetricPoint:
    name: str
    value: float
    timestamp: float
    tags: dict[str, str] = field(default_factory=dict)


class SandboxMetricsCollectorService:
    """Collects and aggregates sandbox runtime metrics."""

    RETENTION_SECONDS = 3600  # 1 hour

    def __init__(self):
        self._metrics: dict[str, list[MetricPoint]] = defaultdict(list)

    def record(self, sandbox_id: str, name: str, value: float,
               tags: dict[str, str] | None = None) -> MetricPoint:
        point = MetricPoint(
            name=name, value=value,
            timestamp=time.time(), tags=tags or {},
        )
        self._metrics[sandbox_id].append(point)
        return point

    def query(self, sandbox_id: str, name: str,
              last_seconds: float = 300) -> list[MetricPoint]:
        cutoff = time.time() - last_seconds
        return [p for p in self._metrics.get(sandbox_id, [])
                if p.name == name and p.timestamp >= cutoff]

    def aggregate(self, sandbox_id: str, name: str,
                  last_seconds: float = 300) -> dict:
        points = self.query(sandbox_id, name, last_seconds)
        if not points:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0, "p95": 0}
        values = sorted(p.value for p in points)
        n = len(values)
        return {
            "count": n,
            "sum": round(sum(values), 3),
            "avg": round(sum(values) / n, 3),
            "min": values[0],
            "max": values[-1],
            "p95": values[int(n * 0.95)] if n > 1 else values[0],
        }

    def list_metric_names(self, sandbox_id: str) -> list[str]:
        names = {p.name for p in self._metrics.get(sandbox_id, [])}
        return sorted(names)

    def get_current(self, sandbox_id: str) -> dict[str, float]:
        """Get latest value for each metric."""
        latest: dict[str, MetricPoint] = {}
        for p in self._metrics.get(sandbox_id, []):
            if p.name not in latest or p.timestamp > latest[p.name].timestamp:
                latest[p.name] = p
        return {name: p.value for name, p in latest.items()}

    def check_threshold(self, sandbox_id: str, name: str,
                        threshold: float) -> dict:
        current = self.get_current(sandbox_id)
        value = current.get(name)
        if value is None:
            return {"exceeded": False, "reason": "No data"}
        return {
            "exceeded": value > threshold,
            "current": value, "threshold": threshold,
            "metric": name,
        }

    def cleanup(self, sandbox_id: str) -> int:
        cutoff = time.time() - self.RETENTION_SECONDS
        before = len(self._metrics.get(sandbox_id, []))
        self._metrics[sandbox_id] = [
            p for p in self._metrics.get(sandbox_id, [])
            if p.timestamp >= cutoff
        ]
        return before - len(self._metrics[sandbox_id])
