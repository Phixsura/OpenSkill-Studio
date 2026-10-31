"""API Request Deduplicator — detect and prevent duplicate API requests."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class DedupeRecord:
    fingerprint: str
    method: str
    path: str
    first_seen: float = field(default_factory=time.time)
    count: int = 1
    last_response_status: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestDeduplicator:
    def __init__(self, window_s: int = 5, max_records: int = 10000) -> None:
        self._records: dict[tuple[str, str], DedupeRecord] = {}
        self._window = max(1, window_s)
        self._max = max(100, max_records)

    def _fingerprint(self, method: str, path: str, body: str, consumer_id: str) -> str:
        content = f"{method}:{path}:{body}:{consumer_id}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def check(self, installation_id: str, method: str, path: str, body: str, consumer_id: str) -> dict[str, object]:
        if not installation_id: raise ValueError("installation_id is required")
        fp = self._fingerprint(method, path, body, consumer_id)
        key = (installation_id, fp)
        now = time.time()
        rec = self._records.get(key)
        if rec and (now - rec.first_seen) < self._window:
            rec.count += 1
            return {"duplicate": True, "fingerprint": fp, "original_status": rec.last_response_status, "count": rec.count}
        rec = DedupeRecord(fingerprint=fp, method=method, path=path)
        self._records[key] = rec
        # Eviction
        if len(self._records) > self._max:
            oldest_key = min(self._records, key=lambda k: self._records[k].first_seen)
            del self._records[oldest_key]
        return {"duplicate": False, "fingerprint": fp}

    def record_response(self, installation_id: str, fingerprint: str, status_code: int) -> None:
        key = (installation_id, fingerprint)
        rec = self._records.get(key)
        if rec: rec.last_response_status = status_code

    def stats(self, installation_id: str) -> dict[str, int]:
        records = [(k, r) for k, r in self._records.items() if k[0] == installation_id]
        total = len(records)
        dupes = sum(1 for _, r in records if r.count > 1)
        return {"total_fingerprints": total, "duplicates_detected": dupes}
