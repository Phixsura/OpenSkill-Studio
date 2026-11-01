"""App API Developer Request Correlation ID — track requests across services."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class CorrelationRecord:
    correlation_id: str
    origin_service: str
    hops: list[str] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed: bool = False

    @property
    def hop_count(self) -> int:
        return len(self.hops)

    @property
    def duration_ms(self) -> float:
        return round((time.time() - self.started_at) * 1000, 1)

class AppAPIDeveloperAPIApiDeveloperApiApiRequestCorrelationId:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], CorrelationRecord] = {}

    def start(self, installation_id: str, correlation_id: str, origin_service: str) -> CorrelationRecord:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, correlation_id)
        if key in self._records: raise ValueError(f"Correlation {correlation_id} exists")
        r = CorrelationRecord(correlation_id=correlation_id, origin_service=origin_service, hops=[origin_service])
        self._records[key] = r
        return r

    def add_hop(self, installation_id: str, correlation_id: str, service: str) -> CorrelationRecord:
        r = self._get(installation_id, correlation_id)
        r.hops.append(service)
        return r

    def complete(self, installation_id: str, correlation_id: str) -> CorrelationRecord:
        r = self._get(installation_id, correlation_id)
        r.completed = True
        return r

    def active(self, installation_id: str) -> list[CorrelationRecord]:
        return [r for (inst, _), r in self._records.items() if inst == installation_id and not r.completed]

    def deep_chains(self, installation_id: str, min_hops: int = 5) -> list[CorrelationRecord]:
        return [r for (inst, _), r in self._records.items() if inst == installation_id and r.hop_count >= min_hops]

    def _get(self, installation_id: str, correlation_id: str) -> CorrelationRecord:
        key = (installation_id, correlation_id)
        r = self._records.get(key)
        if r is None: raise KeyError(f"Correlation {correlation_id} not found")
        return r
