"""API Consumer Request Correlation ID — manage correlation IDs for request tracing."""
from __future__ import annotations
from dataclasses import dataclass, field
import secrets
import time
import structlog

log = structlog.get_logger()

@dataclass
class CorrelationEntry:
    correlation_id: str
    consumer_id: str
    method: str
    path: str
    status_code: int = 0
    duration_ms: float = 0.0
    parent_id: str = ""
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestCorrelationId:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], CorrelationEntry] = {}

    def generate(self, installation_id: str, consumer_id: str, method: str, path: str, parent_id: str = "") -> CorrelationEntry:
        if not installation_id: raise ValueError("installation_id is required")
        cid = f"cor-{secrets.token_hex(12)}"
        entry = CorrelationEntry(correlation_id=cid, consumer_id=consumer_id, method=method, path=path, parent_id=parent_id)
        self._entries[(installation_id, cid)] = entry
        return entry

    def complete(self, installation_id: str, correlation_id: str, status_code: int, duration_ms: float) -> CorrelationEntry:
        key = (installation_id, correlation_id)
        entry = self._entries.get(key)
        if entry is None: raise KeyError(f"Correlation {correlation_id} not found")
        entry.status_code = status_code
        entry.duration_ms = duration_ms
        return entry

    def get_chain(self, installation_id: str, correlation_id: str) -> list[CorrelationEntry]:
        """Get the full correlation chain from root to this entry."""
        chain = []
        current = self._entries.get((installation_id, correlation_id))
        visited: set[str] = set()
        while current and current.correlation_id not in visited:
            chain.append(current)
            visited.add(current.correlation_id)
            if current.parent_id:
                current = self._entries.get((installation_id, current.parent_id))
            else:
                break
        return list(reversed(chain))

    def lookup(self, installation_id: str, correlation_id: str) -> CorrelationEntry | None:
        return self._entries.get((installation_id, correlation_id))

    def entry_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._entries if inst == installation_id)
