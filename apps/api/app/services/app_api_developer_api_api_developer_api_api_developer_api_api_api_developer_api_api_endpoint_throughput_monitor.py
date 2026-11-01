"""App API Developer Endpoint Throughput Monitor — track requests per second per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ThroughputSnapshot:
    endpoint: str
    rps: float  # requests per second
    peak_rps: float = 0.0
    avg_rps: float = 0.0
    samples: int = 0
    total_rps_sum: float = 0.0

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitor:
    def __init__(self) -> None:
        self._snapshots: dict[tuple[str, str], ThroughputSnapshot] = {}

    def record(self, installation_id: str, endpoint: str, rps: float) -> ThroughputSnapshot:
        if not installation_id: raise ValueError("installation_id is required")
        if rps < 0: raise ValueError("rps must be non-negative")
        key = (installation_id, endpoint)
        if key not in self._snapshots:
            self._snapshots[key] = ThroughputSnapshot(endpoint=endpoint, rps=rps, peak_rps=rps)
        s = self._snapshots[key]
        s.rps = rps
        if rps > s.peak_rps: s.peak_rps = rps
        s.samples += 1
        s.total_rps_sum += rps
        s.avg_rps = round(s.total_rps_sum / s.samples, 1)
        return s

    def hottest(self, installation_id: str, limit: int = 5) -> list[ThroughputSnapshot]:
        snaps = [s for (inst, _), s in self._snapshots.items() if inst == installation_id]
        return sorted(snaps, key=lambda s: s.rps, reverse=True)[:limit]

    def above_threshold(self, installation_id: str, threshold_rps: float) -> list[ThroughputSnapshot]:
        return [s for (inst, _), s in self._snapshots.items() if inst == installation_id and s.rps >= threshold_rps]

    def all_endpoints(self, installation_id: str) -> list[ThroughputSnapshot]:
        return [s for (inst, _), s in self._snapshots.items() if inst == installation_id]
