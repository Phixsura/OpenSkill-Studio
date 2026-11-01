"""API Idempotency Key Store — prevent duplicate request processing."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class IdempotencyRecord:
    key: str
    method: str
    path: str
    response_status: int
    response_body: str
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiIdempotencyKeyStore:
    def __init__(self, ttl_seconds: int = 86400) -> None:
        if ttl_seconds < 1: raise ValueError("TTL must be >= 1 second")
        self._ttl = ttl_seconds
        self._store: dict[tuple[str, str], IdempotencyRecord] = {}

    def check(self, installation_id: str, key: str) -> IdempotencyRecord | None:
        if not installation_id: raise ValueError("installation_id is required")
        rec = self._store.get((installation_id, key))
        if rec is None: return None
        if rec.expires_at < time.time():
            del self._store[(installation_id, key)]
            return None
        return rec

    def store(self, installation_id: str, key: str, method: str, path: str, response_status: int, response_body: str) -> IdempotencyRecord:
        if not installation_id: raise ValueError("installation_id is required")
        if not key: raise ValueError("idempotency key is required")
        if len(response_body) > 8192: response_body = response_body[:8192] + "...[TRUNCATED]"
        now = time.time()
        rec = IdempotencyRecord(key=key, method=method, path=path, response_status=response_status, response_body=response_body, created_at=now, expires_at=now + self._ttl)
        self._store[(installation_id, key)] = rec
        return rec

    def evict_expired(self, installation_id: str) -> int:
        now = time.time()
        expired = [(inst, k) for (inst, k), r in self._store.items() if inst == installation_id and r.expires_at < now]
        for k in expired: del self._store[k]
        return len(expired)

    def count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._store if inst == installation_id)

    def delete(self, installation_id: str, key: str) -> bool:
        k = (installation_id, key)
        if k in self._store: del self._store[k]; return True
        return False
