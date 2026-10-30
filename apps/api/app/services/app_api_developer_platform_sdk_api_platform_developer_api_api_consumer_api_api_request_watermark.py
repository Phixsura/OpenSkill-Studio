"""API Consumer Request Watermark — embed traceable watermarks in API responses."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import secrets
import time
import structlog

log = structlog.get_logger()

@dataclass
class Watermark:
    watermark_id: str
    consumer_id: str
    request_id: str
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestWatermark:
    def __init__(self) -> None:
        self._watermarks: dict[tuple[str, str], Watermark] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def generate(self, installation_id: str, consumer_id: str, request_id: str) -> Watermark:
        if not installation_id: raise ValueError("installation_id is required")
        wm_id = hashlib.sha256(f"{installation_id}:{consumer_id}:{request_id}:{secrets.token_hex(8)}".encode()).hexdigest()[:20]
        wm = Watermark(watermark_id=wm_id, consumer_id=consumer_id, request_id=request_id)
        self._watermarks[(installation_id, wm_id)] = wm
        stats = self._stats.setdefault(installation_id, {"generated": 0, "verified": 0})
        stats["generated"] += 1
        return wm

    def verify(self, installation_id: str, watermark_id: str) -> Watermark | None:
        wm = self._watermarks.get((installation_id, watermark_id))
        if wm:
            self._stats.setdefault(installation_id, {"generated": 0, "verified": 0})["verified"] += 1
        return wm

    def trace(self, installation_id: str, watermark_id: str) -> dict[str, str] | None:
        wm = self._watermarks.get((installation_id, watermark_id))
        if wm is None: return None
        return {"watermark_id": wm.watermark_id, "consumer_id": wm.consumer_id, "request_id": wm.request_id}

    def stats(self, installation_id: str) -> dict[str, int]:
        return self._stats.get(installation_id, {"generated": 0, "verified": 0})

    def watermark_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._watermarks if inst == installation_id)
