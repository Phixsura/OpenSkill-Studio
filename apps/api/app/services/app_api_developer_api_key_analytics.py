"""App API Developer API Key Analytics — per-key usage analytics."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class KeyAnalytics:
    key_id: str
    total_requests: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0.0
    last_used: str = ""
    top_endpoint: str = ""

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0: return 0.0
        return round(self.error_count / self.total_requests * 100, 1)

class AppAPIDeveloperAPIKeyAnalytics:
    def __init__(self) -> None:
        self._analytics: dict[tuple[str, str], KeyAnalytics] = {}

    def record(self, installation_id: str, key_id: str, endpoint: str, latency_ms: float, success: bool, day: str = "") -> KeyAnalytics:
        if not installation_id: raise ValueError("installation_id is required")
        k = (installation_id, key_id)
        if k not in self._analytics:
            self._analytics[k] = KeyAnalytics(key_id=key_id)
        a = self._analytics[k]
        a.total_requests += 1
        if not success: a.error_count += 1
        a.avg_latency_ms = round(((a.avg_latency_ms * (a.total_requests - 1)) + latency_ms) / a.total_requests, 1)
        a.top_endpoint = endpoint
        if day: a.last_used = day
        return a

    def get(self, installation_id: str, key_id: str) -> KeyAnalytics:
        a = self._analytics.get((installation_id, key_id))
        if a is None: raise KeyError(f"No analytics for key {key_id}")
        return a

    def top_keys(self, installation_id: str, limit: int = 10) -> list[KeyAnalytics]:
        keys = [a for (inst, _), a in self._analytics.items() if inst == installation_id]
        return sorted(keys, key=lambda a: a.total_requests, reverse=True)[:limit]
