"""App DNS Resolver — resolve and cache DNS lookups for app services.

Manages DNS resolution for installed apps:
- Record DNS lookup results
- TTL-based cache
- Failover tracking
- Per-installation scoped resolvers
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DNSRecord:
    """A cached DNS record."""

    hostname: str
    addresses: list[str]
    ttl_seconds: int
    resolved_at: float = field(default_factory=time.time)
    lookup_ms: float = 0.0
    failed: bool = False
    error: str = ""


class AppDNSResolver:
    """Resolve and cache DNS lookups."""

    def __init__(self) -> None:
        self._cache: dict[tuple[str, str], DNSRecord] = {}

    def record_lookup(
        self,
        installation_id: str,
        hostname: str,
        addresses: list[str],
        ttl_seconds: int = 300,
        lookup_ms: float = 0.0,
        now: float | None = None,
    ) -> DNSRecord:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not hostname:
            raise ValueError("hostname is required")

        record = DNSRecord(
            hostname=hostname, addresses=addresses,
            ttl_seconds=ttl_seconds, resolved_at=now or time.time(),
            lookup_ms=max(0, lookup_ms),
        )
        self._cache[(installation_id, hostname)] = record
        return record

    def record_failure(
        self, installation_id: str, hostname: str, error: str = "",
        now: float | None = None,
    ) -> DNSRecord:
        record = DNSRecord(
            hostname=hostname, addresses=[], ttl_seconds=60,
            resolved_at=now or time.time(), failed=True, error=error,
        )
        self._cache[(installation_id, hostname)] = record
        return record

    def resolve(
        self, installation_id: str, hostname: str, now: float | None = None
    ) -> DNSRecord | None:
        """Get cached record if not expired."""
        now = now or time.time()
        key = (installation_id, hostname)
        record = self._cache.get(key)
        if record is None:
            return None
        if now - record.resolved_at > record.ttl_seconds:
            return None  # expired
        return record

    def is_cached(self, installation_id: str, hostname: str, now: float | None = None) -> bool:
        return self.resolve(installation_id, hostname, now) is not None

    def list_records(self, installation_id: str) -> list[DNSRecord]:
        return [r for (inst, _), r in self._cache.items() if inst == installation_id]

    def failed_lookups(self, installation_id: str) -> list[DNSRecord]:
        return [r for (inst, _), r in self._cache.items()
                if inst == installation_id and r.failed]
