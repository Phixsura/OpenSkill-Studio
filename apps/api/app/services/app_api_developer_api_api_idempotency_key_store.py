"""App API Developer API Idempotency Key Store — manage idempotency keys with TTL."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class IdempotencyRecord:
    key: str
    response_hash: str
    status_code: int
    created_at: float = field(default_factory=time.time)
    ttl_seconds: int = 86400
    hit_count: int = 0

    @property
    def expired(self) -> bool:
        return time.time() > self.created_at + self.ttl_seconds

class AppAPIDeveloperAPIApiIdempotencyKeyStore:
    def __init__(self, default_ttl: int = 86400) -> None:
        self._default_ttl = default_ttl
        self._store: dict[tuple[str, str], IdempotencyRecord] = {}

    def get_or_create(self, installation_id: str, key: str, response_body: str, status_code: int) -> tuple[bool, IdempotencyRecord]:
        if not installation_id: raise ValueError("installation_id is required")
        if not key: raise ValueError("idempotency key is required")
        if len(key) > 256: raise ValueError("key too long (max 256)")
        store_key = (installation_id, key)
        existing = self._store.get(store_key)
        resp_hash = hashlib.sha256(response_body.encode()).hexdigest()[:32]
        if existing and not existing.expired:
            existing.hit_count += 1
            return (True, existing)
        r = IdempotencyRecord(key=key, response_hash=resp_hash, status_code=status_code, ttl_seconds=self._default_ttl)
        self._store[store_key] = r
        return (False, r)

    def exists(self, installation_id: str, key: str) -> bool:
        store_key = (installation_id, key)
        r = self._store.get(store_key)
        return r is not None and not r.expired

    def cleanup(self, installation_id: str) -> int:
        expired = [k for k, r in self._store.items() if k[0] == installation_id and r.expired]
        for k in expired: del self._store[k]
        return len(expired)

    def stats(self, installation_id: str) -> dict[str, int]:
        records = [r for (inst, _), r in self._store.items() if inst == installation_id and not r.expired]
        return {"active_keys": len(records), "total_hits": sum(r.hit_count for r in records)}
