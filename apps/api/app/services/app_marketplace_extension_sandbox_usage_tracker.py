"""Sandbox Usage Tracker — track resource usage over time windows.

Records CPU, memory, disk, network usage per time bucket with rolling
windows, peak detection, quota alerts, and usage forecasting.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class UsageBucket:
    timestamp: float
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    disk_mb: float = 0.0
    network_bytes: int = 0
    api_calls: int = 0


class SandboxUsageTrackerService:
    """Tracks sandbox resource usage across time windows."""

    BUCKET_INTERVAL = 60  # 1 minute buckets
    MAX_BUCKETS = 1440  # 24 hours of data

    def __init__(self):
        self._buckets: dict[str, list[UsageBucket]] = defaultdict(list)

    def record(self, sandbox_id: str, cpu: float = 0, memory_mb: float = 0,
               disk_mb: float = 0, network_bytes: int = 0,
               api_calls: int = 0) -> UsageBucket:
        now = time.time()
        buckets = self._buckets[sandbox_id]

        # Merge into current bucket or create new
        if buckets and now - buckets[-1].timestamp < self.BUCKET_INTERVAL:
            b = buckets[-1]
            b.cpu_percent = max(b.cpu_percent, cpu)
            b.memory_mb = max(b.memory_mb, memory_mb)
            b.disk_mb = max(b.disk_mb, disk_mb)
            b.network_bytes += network_bytes
            b.api_calls += api_calls
        else:
            b = UsageBucket(
                timestamp=now, cpu_percent=cpu, memory_mb=memory_mb,
                disk_mb=disk_mb, network_bytes=network_bytes,
                api_calls=api_calls,
            )
            buckets.append(b)
            if len(buckets) > self.MAX_BUCKETS:
                self._buckets[sandbox_id] = buckets[-self.MAX_BUCKETS:]

        return b

    def get_usage(self, sandbox_id: str, last_minutes: int = 60) -> list[UsageBucket]:
        cutoff = time.time() - last_minutes * 60
        return [b for b in self._buckets.get(sandbox_id, [])
                if b.timestamp >= cutoff]

    def get_peaks(self, sandbox_id: str, last_minutes: int = 60) -> dict:
        buckets = self.get_usage(sandbox_id, last_minutes)
        if not buckets:
            return {"cpu": 0, "memory_mb": 0, "disk_mb": 0, "network_bytes": 0, "api_calls": 0}
        return {
            "cpu": max(b.cpu_percent for b in buckets),
            "memory_mb": max(b.memory_mb for b in buckets),
            "disk_mb": max(b.disk_mb for b in buckets),
            "network_bytes": max(b.network_bytes for b in buckets),
            "api_calls": max(b.api_calls for b in buckets),
        }

    def get_averages(self, sandbox_id: str, last_minutes: int = 60) -> dict:
        buckets = self.get_usage(sandbox_id, last_minutes)
        if not buckets:
            return {"cpu": 0, "memory_mb": 0, "api_calls": 0}
        n = len(buckets)
        return {
            "cpu": round(sum(b.cpu_percent for b in buckets) / n, 1),
            "memory_mb": round(sum(b.memory_mb for b in buckets) / n, 1),
            "api_calls": round(sum(b.api_calls for b in buckets) / n, 1),
        }

    def get_totals(self, sandbox_id: str, last_minutes: int = 60) -> dict:
        buckets = self.get_usage(sandbox_id, last_minutes)
        return {
            "network_bytes": sum(b.network_bytes for b in buckets),
            "api_calls": sum(b.api_calls for b in buckets),
            "bucket_count": len(buckets),
        }

    def forecast(self, sandbox_id: str, metric: str = "api_calls",
                 forecast_minutes: int = 60) -> dict:
        buckets = self.get_usage(sandbox_id, 60)
        if len(buckets) < 2:
            return {"forecast": 0, "confidence": "low"}
        values = [getattr(b, metric, 0) for b in buckets]
        avg = sum(values) / len(values)
        projected = avg * forecast_minutes
        return {
            "forecast": round(projected, 1),
            "based_on_minutes": len(buckets),
            "confidence": "high" if len(buckets) >= 30 else "medium" if len(buckets) >= 10 else "low",
        }
