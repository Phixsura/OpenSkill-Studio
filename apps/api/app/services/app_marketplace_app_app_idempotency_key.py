"""Idempotency key — request deduplication for safe retries."""

import secrets
import hashlib
import html
from datetime import datetime, timezone, timedelta


class IdempotencyStore:
    def __init__(self, *, ttl_s: int = 3600):
        self._store: dict[str, dict] = {}
        self.ttl_s = ttl_s

    def check_or_store(self, *, key: str, request_hash: str) -> dict:
        now = datetime.now(timezone.utc)
        if key in self._store:
            entry = self._store[key]
            if entry["request_hash"] == request_hash:
                return {"duplicate": True, "cached_response": entry.get("response"),
                        "original_at": entry["created_at"]}
            return {"duplicate": True, "conflict": True,
                    "error": "Same key but different request payload"}
        self._store[key] = {"request_hash": request_hash, "created_at": now.isoformat(),
                             "response": None}
        return {"duplicate": False, "key": key}

    def store_response(self, *, key: str, response: dict) -> None:
        if key in self._store:
            self._store[key]["response"] = response

    def stats(self) -> dict:
        return {"stored_keys": len(self._store), "ttl_s": self.ttl_s}


def generate_idempotency_key() -> str:
    return f"idem_{secrets.token_urlsafe(24)}"
