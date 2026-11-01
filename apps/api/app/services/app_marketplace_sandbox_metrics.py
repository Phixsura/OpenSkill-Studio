"""Sandbox Metrics — collect and analyze resource usage from sandbox executions.

Tracks CPU time, memory usage, I/O operations, and execution duration
per extension to enforce quotas and identify performance issues.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ExecutionMetrics:
    extension_id: str
    cpu_ms: float
    memory_mb: float
    io_reads: int
    io_writes: int
    duration_ms: float
    success: bool


class SandboxMetricsCollector:
    """Collects and aggregates sandbox execution metrics."""

    def __init__(self, cpu_quota_ms: float = 60000, memory_quota_mb: float = 512):
        self._metrics: dict[str, list[ExecutionMetrics]] = defaultdict(list)
        self._cpu_quota = cpu_quota_ms
        self._memory_quota = memory_quota_mb

    def record(self, metrics: ExecutionMetrics) -> None:
        self._metrics[metrics.extension_id].append(metrics)

    def get_aggregate(self, extension_id: str) -> dict:
        """Get aggregated metrics for an extension."""
        records = self._metrics.get(extension_id, [])
        if not records:
            return {"extension_id": extension_id, "executions": 0}
        total_cpu = sum(m.cpu_ms for m in records)
        total_mem = sum(m.memory_mb for m in records)
        total_io = sum(m.io_reads + m.io_writes for m in records)
        successes = sum(1 for m in records if m.success)
        return {
            "extension_id": extension_id,
            "executions": len(records),
            "total_cpu_ms": round(total_cpu, 2),
            "avg_cpu_ms": round(total_cpu / len(records), 2),
            "peak_memory_mb": round(max(m.memory_mb for m in records), 2),
            "avg_memory_mb": round(total_mem / len(records), 2),
            "total_io_ops": total_io,
            "success_rate": round(successes / len(records), 4),
            "avg_duration_ms": round(sum(m.duration_ms for m in records) / len(records), 2),
        }

    def check_quota(self, extension_id: str) -> dict:
        """Check if extension is within resource quotas."""
        records = self._metrics.get(extension_id, [])
        total_cpu = sum(m.cpu_ms for m in records)
        peak_mem = max((m.memory_mb for m in records), default=0)
        return {
            "extension_id": extension_id,
            "cpu_used_ms": round(total_cpu, 2),
            "cpu_quota_ms": self._cpu_quota,
            "cpu_remaining_ms": round(max(0, self._cpu_quota - total_cpu), 2),
            "cpu_exceeded": total_cpu > self._cpu_quota,
            "memory_peak_mb": round(peak_mem, 2),
            "memory_quota_mb": self._memory_quota,
            "memory_exceeded": peak_mem > self._memory_quota,
        }

    def get_top_consumers(self, metric: str = "cpu", limit: int = 10) -> list[tuple[str, float]]:
        """Get top resource-consuming extensions."""
        totals: dict[str, float] = {}
        for ext_id, records in self._metrics.items():
            if metric == "cpu":
                totals[ext_id] = sum(m.cpu_ms for m in records)
            elif metric == "memory":
                totals[ext_id] = max(m.memory_mb for m in records)
            elif metric == "io":
                totals[ext_id] = sum(m.io_reads + m.io_writes for m in records)
        return sorted(totals.items(), key=lambda x: x[1], reverse=True)[:limit]

    def clear(self, extension_id: str) -> None:
        self._metrics.pop(extension_id, None)
