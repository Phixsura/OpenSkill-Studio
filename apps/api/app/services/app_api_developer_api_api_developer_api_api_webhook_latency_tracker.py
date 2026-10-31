"""App API Developer Webhook Latency Tracker — track delivery latency per destination."""
from __future__ import annotations
from dataclasses import dataclass, field
import bisect
import structlog

log = structlog.get_logger()

@dataclass
class LatencyStats:
    destination: str
    samples: list[float] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.samples)

    @property
    def avg_ms(self) -> float:
        return round(sum(self.samples) / len(self.samples), 1) if self.samples else 0.0

    @property
    def p50_ms(self) -> float:
        if not self.samples: return 0.0
        return self.samples[len(self.samples) // 2]

    @property
    def p99_ms(self) -> float:
        if not self.samples: return 0.0
        return self.samples[min(int(len(self.samples) * 0.99), len(self.samples) - 1)]

class AppAPIDeveloperAPIApiDeveloperApiApiWebhookLatencyTracker:
    def __init__(self) -> None:
        self._stats: dict[tuple[str, str], LatencyStats] = {}

    def record(self, installation_id: str, destination: str, latency_ms: float) -> LatencyStats:
        if not installation_id: raise ValueError("installation_id is required")
        if latency_ms < 0: raise ValueError("latency must be non-negative")
        key = (installation_id, destination)
        if key not in self._stats:
            self._stats[key] = LatencyStats(destination=destination)
        s = self._stats[key]
        bisect.insort(s.samples, latency_ms)
        return s

    def get(self, installation_id: str, destination: str) -> LatencyStats | None:
        return self._stats.get((installation_id, destination))

    def slowest(self, installation_id: str, limit: int = 5) -> list[LatencyStats]:
        stats = [s for (inst, _), s in self._stats.items() if inst == installation_id]
        return sorted(stats, key=lambda s: s.p99_ms, reverse=True)[:limit]

    def all_destinations(self, installation_id: str) -> list[LatencyStats]:
        return [s for (inst, _), s in self._stats.items() if inst == installation_id]
