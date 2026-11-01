"""API Consumer Request Coalescer — coalesce duplicate concurrent requests."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class CoalescedRequest:
    fingerprint: str
    method: str
    path: str
    waiting_count: int = 1
    resolved: bool = False
    result_status: int = 0
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCoalescer:
    def __init__(self, window_ms: int = 100) -> None:
        self._pending: dict[tuple[str, str], CoalescedRequest] = {}
        self._window = max(10, window_ms) / 1000
        self._stats: dict[str, dict[str, int]] = {}

    def coalesce(self, installation_id: str, method: str, path: str, consumer_id: str) -> tuple[CoalescedRequest, bool]:
        """Returns (request, is_leader). Leader processes, followers wait."""
        if not installation_id: raise ValueError("installation_id is required")
        fp = hashlib.sha256(f"{method}:{path}:{consumer_id}".encode()).hexdigest()[:16]
        key = (installation_id, fp)
        now = time.time()
        existing = self._pending.get(key)
        if existing and not existing.resolved and (now - existing.created_at) < self._window:
            existing.waiting_count += 1
            stats = self._stats.setdefault(installation_id, {"coalesced": 0, "total": 0})
            stats["coalesced"] += 1
            stats["total"] += 1
            return existing, False
        req = CoalescedRequest(fingerprint=fp, method=method, path=path)
        self._pending[key] = req
        stats = self._stats.setdefault(installation_id, {"coalesced": 0, "total": 0})
        stats["total"] += 1
        return req, True

    def resolve(self, installation_id: str, fingerprint: str, status: int) -> CoalescedRequest:
        key = (installation_id, fingerprint)
        req = self._pending.get(key)
        if req is None: raise KeyError(f"Request {fingerprint} not found")
        req.resolved = True
        req.result_status = status
        return req

    def coalesce_rate(self, installation_id: str) -> float:
        s = self._stats.get(installation_id, {"coalesced": 0, "total": 0})
        if s["total"] == 0: return 0.0
        return round((s["coalesced"] / s["total"]) * 100, 1)

    def pending_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _), r in self._pending.items() if inst == installation_id and not r.resolved)
