"""API Consumer Webhook Acknowledgment — track webhook delivery acknowledgments."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class AckRecord:
    event_id: str
    consumer_id: str
    acknowledged: bool = False
    ack_latency_ms: float = 0.0
    delivered_at: float = field(default_factory=time.time)
    acked_at: float = 0.0
    retry_count: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookAcknowledgment:
    def __init__(self, ack_timeout_s: int = 30) -> None:
        self._records: dict[tuple[str, str, str], AckRecord] = {}
        self._timeout = max(5, ack_timeout_s)
        self._stats: dict[str, dict[str, int]] = {}

    def record_delivery(self, installation_id: str, event_id: str, consumer_id: str) -> AckRecord:
        if not installation_id: raise ValueError("installation_id is required")
        rec = AckRecord(event_id=event_id, consumer_id=consumer_id)
        self._records[(installation_id, consumer_id, event_id)] = rec
        return rec

    def acknowledge(self, installation_id: str, consumer_id: str, event_id: str) -> AckRecord:
        key = (installation_id, consumer_id, event_id)
        rec = self._records.get(key)
        if rec is None: raise KeyError(f"No delivery record for {event_id}")
        if rec.acknowledged: return rec
        now = time.time()
        rec.acknowledged = True
        rec.acked_at = now
        rec.ack_latency_ms = round((now - rec.delivered_at) * 1000, 2)
        stats = self._stats.setdefault(installation_id, {"acked": 0, "unacked": 0})
        stats["acked"] += 1
        return rec

    def unacknowledged(self, installation_id: str, consumer_id: str | None = None) -> list[AckRecord]:
        now = time.time()
        records = [r for (inst, _, _), r in self._records.items() if inst == installation_id and not r.acknowledged and (now - r.delivered_at) > self._timeout]
        if consumer_id: records = [r for r in records if r.consumer_id == consumer_id]
        return records

    def ack_rate(self, installation_id: str) -> float:
        total = sum(1 for (inst, _, _) in self._records if inst == installation_id)
        acked = sum(1 for (inst, _, _), r in self._records.items() if inst == installation_id and r.acknowledged)
        return round((acked / total) * 100, 1) if total > 0 else 0.0

    def avg_ack_latency(self, installation_id: str) -> float:
        acked = [r for (inst, _, _), r in self._records.items() if inst == installation_id and r.acknowledged]
        if not acked: return 0.0
        return round(sum(r.ack_latency_ms for r in acked) / len(acked), 2)
