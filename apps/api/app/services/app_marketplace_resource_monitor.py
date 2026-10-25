"""Resource Monitor — real-time resource tracking for sandboxed extensions.

Collects time-series resource samples (CPU, memory, I/O, network)
and provides aggregation, alerting, and trend analysis.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ResourceSample:
    timestamp: str
    cpu_percent: float
    memory_mb: float
    disk_io_ops: int
    network_bytes: int


class ResourceMonitor:
    """Collects and analyzes time-series resource usage data."""

    def __init__(self, alert_cpu: float = 90.0, alert_memory_mb: float = 450.0):
        self._samples: dict[str, list[ResourceSample]] = defaultdict(list)
        self._alert_cpu = alert_cpu
        self._alert_memory = alert_memory_mb
        self._alerts: list[dict] = []

    def record_sample(self, extension_id: str, cpu: float, memory_mb: float,
                      disk_io: int = 0, network_bytes: int = 0) -> ResourceSample:
        """Record a resource usage sample."""
        sample = ResourceSample(
            timestamp=datetime.now(timezone.utc).isoformat(),
            cpu_percent=cpu, memory_mb=memory_mb,
            disk_io_ops=disk_io, network_bytes=network_bytes,
        )
        self._samples[extension_id].append(sample)

        # Check alerts
        if cpu > self._alert_cpu:
            self._alerts.append({"extension_id": extension_id, "type": "cpu_high",
                                  "value": cpu, "threshold": self._alert_cpu})
        if memory_mb > self._alert_memory:
            self._alerts.append({"extension_id": extension_id, "type": "memory_high",
                                  "value": memory_mb, "threshold": self._alert_memory})
        return sample

    def get_latest(self, extension_id: str) -> ResourceSample | None:
        samples = self._samples.get(extension_id, [])
        return samples[-1] if samples else None

    def get_averages(self, extension_id: str, last_n: int = 60) -> dict:
        """Get average resource usage over last N samples."""
        samples = self._samples.get(extension_id, [])[-last_n:]
        if not samples:
            return {"cpu": 0, "memory": 0, "disk_io": 0, "network": 0, "sample_count": 0}
        n = len(samples)
        return {
            "cpu": round(sum(s.cpu_percent for s in samples) / n, 2),
            "memory": round(sum(s.memory_mb for s in samples) / n, 2),
            "disk_io": sum(s.disk_io_ops for s in samples) // n,
            "network": sum(s.network_bytes for s in samples) // n,
            "sample_count": n,
        }

    def get_peaks(self, extension_id: str) -> dict:
        """Get peak resource usage."""
        samples = self._samples.get(extension_id, [])
        if not samples:
            return {"cpu": 0, "memory": 0, "disk_io": 0, "network": 0}
        return {
            "cpu": round(max(s.cpu_percent for s in samples), 2),
            "memory": round(max(s.memory_mb for s in samples), 2),
            "disk_io": max(s.disk_io_ops for s in samples),
            "network": max(s.network_bytes for s in samples),
        }

    def get_trend(self, extension_id: str, metric: str = "cpu",
                  window: int = 10) -> str:
        """Detect trend: increasing, decreasing, or stable."""
        samples = self._samples.get(extension_id, [])
        if len(samples) < window * 2:
            return "insufficient_data"
        getter = {"cpu": lambda s: s.cpu_percent, "memory": lambda s: s.memory_mb}.get(metric)
        if not getter:
            return "unknown_metric"
        first_half = sum(getter(s) for s in samples[-window*2:-window]) / window
        second_half = sum(getter(s) for s in samples[-window:]) / window
        change = (second_half - first_half) / max(0.01, first_half)
        if change > 0.1:
            return "increasing"
        elif change < -0.1:
            return "decreasing"
        return "stable"

    def get_alerts(self, extension_id: str | None = None) -> list[dict]:
        if extension_id:
            return [a for a in self._alerts if a["extension_id"] == extension_id]
        return list(self._alerts)

    def clear_samples(self, extension_id: str) -> int:
        count = len(self._samples.get(extension_id, []))
        self._samples.pop(extension_id, None)
        return count
