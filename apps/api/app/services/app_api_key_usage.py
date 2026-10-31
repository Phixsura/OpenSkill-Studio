"""App API Key Usage — track per-key API usage analytics.

Manages API key usage:
- Record requests per key
- Track by endpoint and status
- Daily usage summaries
- Per-installation scoped usage
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class KeyUsageRecord:
    """Usage record for an API key."""

    key_id: str
    total_requests: int = 0
    success_count: int = 0
    error_count: int = 0
    endpoints: dict[str, int] = field(default_factory=dict)

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return round(self.error_count / self.total_requests * 100, 1)


class AppAPIKeyUsage:
    """Track per-key API usage analytics."""

    def __init__(self) -> None:
        self._usage: dict[tuple[str, str], KeyUsageRecord] = {}

    def record(
        self, installation_id: str, key_id: str, endpoint: str,
        success: bool,
    ) -> KeyUsageRecord:
        if not installation_id:
            raise ValueError("installation_id is required")

        k = (installation_id, key_id)
        if k not in self._usage:
            self._usage[k] = KeyUsageRecord(key_id=key_id)

        usage = self._usage[k]
        usage.total_requests += 1
        if success:
            usage.success_count += 1
        else:
            usage.error_count += 1
        usage.endpoints[endpoint] = usage.endpoints.get(endpoint, 0) + 1
        return usage

    def get_usage(self, installation_id: str, key_id: str) -> KeyUsageRecord:
        k = (installation_id, key_id)
        u = self._usage.get(k)
        if u is None:
            raise KeyError(f"No usage for key {key_id}")
        return u

    def top_keys(self, installation_id: str, limit: int = 10) -> list[KeyUsageRecord]:
        keys = [u for (inst, _), u in self._usage.items() if inst == installation_id]
        return sorted(keys, key=lambda u: u.total_requests, reverse=True)[:limit]

    def top_endpoints(self, installation_id: str, key_id: str) -> list[dict]:
        u = self.get_usage(installation_id, key_id)
        return sorted(
            [{"endpoint": e, "count": c} for e, c in u.endpoints.items()],
            key=lambda x: x["count"], reverse=True,
        )
