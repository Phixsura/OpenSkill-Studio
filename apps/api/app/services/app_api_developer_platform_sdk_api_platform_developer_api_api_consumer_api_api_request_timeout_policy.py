"""API Consumer Request Timeout Policy — configurable timeout policies per endpoint."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class TimeoutPolicy:
    endpoint: str
    method: str
    timeout_ms: int = 30000
    retry_on_timeout: bool = False
    max_retries: int = 1

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestTimeoutPolicy:
    def __init__(self, default_timeout_ms: int = 30000) -> None:
        self._policies: dict[tuple[str, str, str], TimeoutPolicy] = {}
        self._default = max(1000, default_timeout_ms)
        self._stats: dict[str, dict[str, int]] = {}

    def set_policy(self, installation_id: str, policy: TimeoutPolicy) -> TimeoutPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        if policy.timeout_ms < 100: raise ValueError("timeout must be >= 100ms")
        if policy.max_retries < 0: raise ValueError("max_retries must be >= 0")
        self._policies[(installation_id, policy.method.upper(), policy.endpoint)] = policy
        return policy

    def get_timeout(self, installation_id: str, method: str, endpoint: str) -> int:
        p = self._policies.get((installation_id, method.upper(), endpoint))
        return p.timeout_ms if p else self._default

    def should_retry(self, installation_id: str, method: str, endpoint: str, attempt: int) -> bool:
        p = self._policies.get((installation_id, method.upper(), endpoint))
        if p is None: return False
        return p.retry_on_timeout and attempt < p.max_retries

    def record_timeout(self, installation_id: str, method: str, endpoint: str) -> None:
        stats = self._stats.setdefault(installation_id, {"timeouts": 0})
        stats["timeouts"] += 1

    def timeout_count(self, installation_id: str) -> int:
        return self._stats.get(installation_id, {"timeouts": 0})["timeouts"]

    def list_policies(self, installation_id: str) -> list[TimeoutPolicy]:
        return [p for (inst, _, _), p in self._policies.items() if inst == installation_id]
