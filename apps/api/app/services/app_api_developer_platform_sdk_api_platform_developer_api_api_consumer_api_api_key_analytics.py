"""API Consumer API Key Analytics — track per-key usage analytics."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class KeyUsage:
    key_id: str
    consumer_id: str
    total_requests: int = 0
    success_count: int = 0
    error_count: int = 0
    last_used_endpoint: str = ""
    unique_endpoints: set[str] = field(default_factory=set)

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0: return 0.0
        return round((self.error_count / self.total_requests) * 100, 1)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyAnalytics:
    def __init__(self) -> None:
        self._usage: dict[tuple[str, str], KeyUsage] = {}

    def record(self, installation_id: str, key_id: str, consumer_id: str, endpoint: str, success: bool) -> KeyUsage:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, key_id)
        u = self._usage.get(key)
        if u is None:
            u = KeyUsage(key_id=key_id, consumer_id=consumer_id)
            self._usage[key] = u
        u.total_requests += 1
        u.last_used_endpoint = endpoint
        u.unique_endpoints.add(endpoint)
        if success: u.success_count += 1
        else: u.error_count += 1
        return u

    def get_usage(self, installation_id: str, key_id: str) -> KeyUsage | None:
        return self._usage.get((installation_id, key_id))

    def top_keys(self, installation_id: str, limit: int = 5) -> list[KeyUsage]:
        keys = [u for (inst, _), u in self._usage.items() if inst == installation_id]
        return sorted(keys, key=lambda u: -u.total_requests)[:limit]

    def inactive_keys(self, installation_id: str, min_requests: int = 0) -> list[KeyUsage]:
        return [u for (inst, _), u in self._usage.items() if inst == installation_id and u.total_requests <= min_requests]

    def key_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._usage if inst == installation_id)
