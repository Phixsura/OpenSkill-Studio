"""Consumer API Webhook Dedup — content-hash based webhook deduplication."""
from __future__ import annotations

import hashlib
import json
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class DedupEntry:
    fingerprint: str
    webhook_id: str
    event_type: str
    first_seen: float
    count: int = 1


@dataclass
class WebhookDedup:
    """Deduplicate webhooks based on content fingerprinting."""

    _seen: dict[str, DedupEntry] = field(default_factory=dict)
    _ttl_seconds: float = 3600.0
    _total_checked: int = 0
    _total_deduped: int = 0

    def configure(self, ttl_seconds: float = 3600.0) -> dict:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._ttl_seconds = ttl_seconds
        return {"ttl_seconds": ttl_seconds}

    def _fingerprint(self, webhook_id: str, event_type: str, payload: dict) -> str:
        content = json.dumps({"w": webhook_id, "e": event_type, "p": payload},
                             sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def check(self, webhook_id: str, event_type: str, payload: dict,
              current_time: float = 0.0) -> dict:
        self._total_checked += 1
        fp = self._fingerprint(webhook_id, event_type, payload)
        existing = self._seen.get(fp)
        if existing:
            age = current_time - existing.first_seen
            if age < self._ttl_seconds:
                existing.count += 1
                self._total_deduped += 1
                return {"duplicate": True, "fingerprint": fp,
                        "first_seen_ago": round(age, 1), "count": existing.count}
            else:
                # TTL expired, treat as new
                del self._seen[fp]
        self._seen[fp] = DedupEntry(
            fingerprint=fp, webhook_id=webhook_id,
            event_type=event_type, first_seen=current_time,
        )
        return {"duplicate": False, "fingerprint": fp}

    def cleanup(self, current_time: float = 0.0) -> dict:
        expired = [fp for fp, entry in self._seen.items()
                   if current_time - entry.first_seen >= self._ttl_seconds]
        for fp in expired:
            del self._seen[fp]
        return {"removed": len(expired), "remaining": len(self._seen)}

    def get_recent_dupes(self, limit: int = 20) -> list[dict]:
        dupes = [e for e in self._seen.values() if e.count > 1]
        dupes.sort(key=lambda x: x.count, reverse=True)
        return [
            {"fingerprint": e.fingerprint, "webhook_id": e.webhook_id,
             "event_type": e.event_type, "count": e.count}
            for e in dupes[:limit]
        ]

    def get_stats(self) -> dict:
        return {
            "total_checked": self._total_checked,
            "total_deduped": self._total_deduped,
            "dedup_rate": round(self._total_deduped / self._total_checked * 100, 1)
            if self._total_checked > 0 else 0,
            "active_fingerprints": len(self._seen),
            "ttl_seconds": self._ttl_seconds,
        }
