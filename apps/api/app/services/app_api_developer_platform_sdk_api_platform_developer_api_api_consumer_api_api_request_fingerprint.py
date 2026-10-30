"""API Consumer Request Fingerprint — fingerprint requests for dedup and analytics."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class Fingerprint:
    fingerprint_id: str
    method: str
    path: str
    consumer_id: str
    body_hash: str
    hit_count: int = 1
    first_seen: float = 0.0
    last_seen: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestFingerprint:
    def __init__(self) -> None:
        self._fingerprints: dict[tuple[str, str], Fingerprint] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def fingerprint(self, installation_id: str, method: str, path: str, consumer_id: str, body: str = "") -> Fingerprint:
        if not installation_id: raise ValueError("installation_id is required")
        import time
        body_hash = hashlib.sha256(body.encode()).hexdigest()[:12]
        fp_id = hashlib.sha256(f"{method}:{path}:{consumer_id}:{body_hash}".encode()).hexdigest()[:16]
        key = (installation_id, fp_id)
        now = time.time()
        existing = self._fingerprints.get(key)
        stats = self._stats.setdefault(installation_id, {"unique": 0, "total": 0})
        stats["total"] += 1
        if existing:
            existing.hit_count += 1
            existing.last_seen = now
            return existing
        fp = Fingerprint(fingerprint_id=fp_id, method=method, path=path, consumer_id=consumer_id, body_hash=body_hash, first_seen=now, last_seen=now)
        self._fingerprints[key] = fp
        stats["unique"] += 1
        return fp

    def top_fingerprints(self, installation_id: str, limit: int = 10) -> list[Fingerprint]:
        fps = [fp for (inst, _), fp in self._fingerprints.items() if inst == installation_id]
        return sorted(fps, key=lambda f: -f.hit_count)[:limit]

    def unique_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._fingerprints if inst == installation_id)

    def dedup_ratio(self, installation_id: str) -> float:
        s = self._stats.get(installation_id, {"unique": 0, "total": 0})
        if s["total"] == 0: return 0.0
        return round((1 - s["unique"] / s["total"]) * 100, 1)
