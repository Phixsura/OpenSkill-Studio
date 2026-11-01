"""Request Deduplication — detect and reject duplicate requests using idempotency keys."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class DeduplicationEntry:
    idempotency_key: str
    request_hash: str
    response_status: int
    response_body_hash: str
    created_at: datetime
    expires_at: datetime

@dataclass
class DeduplicationResult:
    is_duplicate: bool
    idempotency_key: str
    original_status: int | None = None
    original_body_hash: str | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestDeduplication:
    def __init__(self, ttl_hours: int = 24) -> None:
        self._entries: dict[tuple[str, str, str], DeduplicationEntry] = {}  # (inst, consumer, key)
        self._ttl_hours = ttl_hours

    def check(self, installation_id: str, consumer_id: str, idempotency_key: str, now: datetime) -> DeduplicationResult:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, consumer_id, idempotency_key)
        entry = self._entries.get(key)
        if entry and now < entry.expires_at:
            return DeduplicationResult(is_duplicate=True, idempotency_key=idempotency_key, original_status=entry.response_status, original_body_hash=entry.response_body_hash)
        return DeduplicationResult(is_duplicate=False, idempotency_key=idempotency_key)

    def record(self, installation_id: str, consumer_id: str, idempotency_key: str, request_hash: str, response_status: int, response_body_hash: str, now: datetime) -> DeduplicationEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        entry = DeduplicationEntry(
            idempotency_key=idempotency_key, request_hash=request_hash,
            response_status=response_status, response_body_hash=response_body_hash,
            created_at=now, expires_at=now + timedelta(hours=self._ttl_hours),
        )
        self._entries[(installation_id, consumer_id, idempotency_key)] = entry
        log.info("dedup_recorded", installation_id=installation_id, consumer_id=consumer_id, key=idempotency_key)
        return entry

    def cleanup(self, now: datetime) -> int:
        expired = [k for k, e in self._entries.items() if now >= e.expires_at]
        for k in expired:
            del self._entries[k]
        return len(expired)

    @staticmethod
    def hash_request(method: str, path: str, body: str) -> str:
        return hashlib.sha256(f"{method}:{path}:{body}".encode()).hexdigest()[:16]
