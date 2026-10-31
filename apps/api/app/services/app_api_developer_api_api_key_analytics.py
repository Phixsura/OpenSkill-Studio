"""App API Developer API Key Analytics — per-key usage tracking."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class KeyUsage:
    key_id: str
    key_prefix: str  # first 8 chars only
    total_requests: int = 0
    last_used_at: float = 0.0
    endpoints_hit: dict[str, int] = field(default_factory=dict)
    error_count: int = 0

class AppAPIDeveloperAPIApiKeyAnalytics:
    def __init__(self) -> None:
        self._usage: dict[tuple[str, str], KeyUsage] = {}

    def track(self, installation_id: str, key_id: str, key_prefix: str, endpoint: str, success: bool) -> KeyUsage:
        if not installation_id: raise ValueError("installation_id is required")
        if len(key_prefix) > 8: key_prefix = key_prefix[:8]
        key = (installation_id, key_id)
        if key not in self._usage:
            self._usage[key] = KeyUsage(key_id=key_id, key_prefix=key_prefix)
        u = self._usage[key]
        u.total_requests += 1
        u.last_used_at = time.time()
        u.endpoints_hit[endpoint] = u.endpoints_hit.get(endpoint, 0) + 1
        if not success: u.error_count += 1
        return u

    def get(self, installation_id: str, key_id: str) -> KeyUsage | None:
        return self._usage.get((installation_id, key_id))

    def top_keys(self, installation_id: str, limit: int = 10) -> list[KeyUsage]:
        keys = [u for (inst, _), u in self._usage.items() if inst == installation_id]
        return sorted(keys, key=lambda u: u.total_requests, reverse=True)[:limit]

    def inactive_keys(self, installation_id: str, since: float = 0.0) -> list[KeyUsage]:
        return [u for (inst, _), u in self._usage.items() if inst == installation_id and u.last_used_at < since]
