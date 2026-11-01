"""API Consumer Webhook Event Deduplicator — prevent duplicate event delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class DedupeResult:
    event_id: str
    is_duplicate: bool
    fingerprint: str
    first_seen: bool = True

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventDeduplicator:
    def __init__(self, window_s: int = 3600) -> None:
        self._seen: dict[tuple[str, str, str], float] = {}  # (inst, consumer, fingerprint) → timestamp
        self._window = max(60, window_s)
        self._stats: dict[str, dict[str, int]] = {}

    def check(self, installation_id: str, consumer_id: str, event_id: str, payload: str) -> DedupeResult:
        if not installation_id: raise ValueError("installation_id is required")
        fp = hashlib.sha256(f"{consumer_id}:{payload}".encode()).hexdigest()[:16]
        key = (installation_id, consumer_id, fp)
        now = time.time()
        stats = self._stats.setdefault(installation_id, {"checked": 0, "duplicates": 0})
        stats["checked"] += 1
        last_seen = self._seen.get(key)
        if last_seen and (now - last_seen) < self._window:
            stats["duplicates"] += 1
            return DedupeResult(event_id=event_id, is_duplicate=True, fingerprint=fp, first_seen=False)
        self._seen[key] = now
        return DedupeResult(event_id=event_id, is_duplicate=False, fingerprint=fp, first_seen=True)

    def stats(self, installation_id: str) -> dict[str, int]:
        return self._stats.get(installation_id, {"checked": 0, "duplicates": 0})

    def duplicate_rate(self, installation_id: str) -> float:
        s = self.stats(installation_id)
        if s["checked"] == 0: return 0.0
        return round((s["duplicates"] / s["checked"]) * 100, 1)
