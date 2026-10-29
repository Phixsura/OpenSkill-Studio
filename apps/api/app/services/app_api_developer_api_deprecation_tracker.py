"""App API Developer Deprecation Tracker — track deprecated endpoint usage."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class DeprecatedEndpoint:
    endpoint: str
    deprecated_at: float
    sunset_at: float  # when it will be removed
    replacement: str = ""
    hit_count: int = 0
    unique_consumers: set[str] = field(default_factory=set)

    @property
    def days_until_sunset(self) -> float:
        return max(0.0, round((self.sunset_at - time.time()) / 86400, 1))

class AppAPIDeveloperAPIDeprecationTracker:
    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str], DeprecatedEndpoint] = {}

    def deprecate(self, installation_id: str, endpoint: str, sunset_at: float, replacement: str = "") -> DeprecatedEndpoint:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, endpoint)
        if key in self._endpoints: raise ValueError(f"{endpoint} already deprecated")
        d = DeprecatedEndpoint(endpoint=endpoint, deprecated_at=time.time(), sunset_at=sunset_at, replacement=replacement)
        self._endpoints[key] = d
        return d

    def record_hit(self, installation_id: str, endpoint: str, consumer_id: str) -> DeprecatedEndpoint:
        key = (installation_id, endpoint)
        d = self._endpoints.get(key)
        if d is None: raise KeyError(f"{endpoint} not deprecated")
        d.hit_count += 1
        d.unique_consumers.add(consumer_id)
        return d

    def active(self, installation_id: str) -> list[DeprecatedEndpoint]:
        now = time.time()
        return [d for (inst, _), d in self._endpoints.items() if inst == installation_id and d.sunset_at > now]

    def past_sunset(self, installation_id: str) -> list[DeprecatedEndpoint]:
        now = time.time()
        return [d for (inst, _), d in self._endpoints.items() if inst == installation_id and d.sunset_at <= now]

    def most_used(self, installation_id: str, limit: int = 5) -> list[DeprecatedEndpoint]:
        deps = [d for (inst, _), d in self._endpoints.items() if inst == installation_id]
        return sorted(deps, key=lambda d: d.hit_count, reverse=True)[:limit]
