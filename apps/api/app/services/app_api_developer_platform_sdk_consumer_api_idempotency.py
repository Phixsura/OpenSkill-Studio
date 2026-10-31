"""Consumer Idempotency Manager — idempotent request handling with key tracking."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class IdempotencyRecord:
    key: str
    consumer_id: str
    status_code: int
    response_body: dict | str
    created_at: float
    expires_at: float


@dataclass
class IdempotencyManager:
    """Track idempotency keys to prevent duplicate request processing."""

    _records: dict[str, IdempotencyRecord] = field(default_factory=dict)
    _default_ttl: float = 86400.0  # 24 hours
    _max_records: int = 100000

    def configure(self, default_ttl: float = 86400.0, max_records: int = 100000) -> dict:
        if default_ttl <= 0:
            raise ValueError("TTL must be positive")
        self._default_ttl = default_ttl
        self._max_records = max_records
        return {"default_ttl": default_ttl, "max_records": max_records}

    def check(self, key: str, consumer_id: str, current_time: float = 0.0) -> dict:
        record = self._records.get(key)
        if not record:
            return {"exists": False}
        if record.consumer_id != consumer_id:
            return {"exists": False, "reason": "different_consumer"}
        if current_time > record.expires_at:
            del self._records[key]
            return {"exists": False, "reason": "expired"}
        return {
            "exists": True,
            "status_code": record.status_code,
            "response_body": record.response_body,
            "age_seconds": round(current_time - record.created_at, 1),
        }

    def store(self, key: str, consumer_id: str, status_code: int,
              response_body: dict | str, current_time: float = 0.0,
              ttl: float | None = None) -> dict:
        if len(self._records) >= self._max_records:
            self._evict_oldest()
        actual_ttl = ttl if ttl is not None else self._default_ttl
        self._records[key] = IdempotencyRecord(
            key=key, consumer_id=consumer_id,
            status_code=status_code, response_body=response_body,
            created_at=current_time, expires_at=current_time + actual_ttl,
        )
        logger.info("idempotency_stored", key=key, consumer_id=consumer_id)
        return {"key": key, "stored": True, "expires_in": actual_ttl}

    def _evict_oldest(self) -> None:
        if not self._records:
            return
        oldest_key = min(self._records, key=lambda k: self._records[k].created_at)
        del self._records[oldest_key]

    def delete(self, key: str) -> dict:
        if key in self._records:
            del self._records[key]
            return {"deleted": True}
        return {"deleted": False}

    def cleanup_expired(self, current_time: float = 0.0) -> dict:
        expired = [k for k, r in self._records.items() if current_time > r.expires_at]
        for k in expired:
            del self._records[k]
        return {"removed": len(expired), "remaining": len(self._records)}

    def get_consumer_keys(self, consumer_id: str) -> list[dict]:
        return [
            {"key": r.key, "status_code": r.status_code, "created_at": r.created_at}
            for r in self._records.values() if r.consumer_id == consumer_id
        ]

    def get_stats(self) -> dict:
        return {
            "total_records": len(self._records),
            "max_records": self._max_records,
            "usage_pct": round(len(self._records) / self._max_records * 100, 1)
            if self._max_records > 0 else 0,
        }
