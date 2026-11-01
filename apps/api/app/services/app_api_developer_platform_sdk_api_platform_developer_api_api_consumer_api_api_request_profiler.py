"""API Consumer Request Profiler — profile request performance characteristics."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class RequestProfile:
    endpoint: str
    method: str
    samples: int = 0
    min_ms: float = float("inf")
    max_ms: float = 0.0
    total_ms: float = 0.0
    p50_estimate: float = 0.0
    error_count: int = 0

    @property
    def avg_ms(self) -> float:
        if self.samples == 0: return 0.0
        return round(self.total_ms / self.samples, 2)

    @property
    def error_pct(self) -> float:
        if self.samples == 0: return 0.0
        return round((self.error_count / self.samples) * 100, 1)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestProfiler:
    def __init__(self) -> None:
        self._profiles: dict[tuple[str, str, str], RequestProfile] = {}

    def record(self, installation_id: str, endpoint: str, method: str, latency_ms: float, error: bool = False) -> RequestProfile:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        p = self._profiles.get(key)
        if p is None:
            p = RequestProfile(endpoint=endpoint, method=method.upper())
            self._profiles[key] = p
        p.samples += 1
        p.total_ms += latency_ms
        p.min_ms = min(p.min_ms, latency_ms)
        p.max_ms = max(p.max_ms, latency_ms)
        p.p50_estimate = p.avg_ms  # running estimate
        if error: p.error_count += 1
        return p

    def slowest(self, installation_id: str, limit: int = 5) -> list[RequestProfile]:
        profiles = [p for (inst, _, _), p in self._profiles.items() if inst == installation_id]
        return sorted(profiles, key=lambda p: -p.avg_ms)[:limit]

    def get_profile(self, installation_id: str, method: str, endpoint: str) -> RequestProfile | None:
        return self._profiles.get((installation_id, method.upper(), endpoint))

    def list_profiles(self, installation_id: str) -> list[RequestProfile]:
        return [p for (inst, _, _), p in self._profiles.items() if inst == installation_id]
