"""Consumer API Webhook Event Replay — replay past webhook events for debugging."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import json
import structlog

log = structlog.get_logger()

@dataclass
class ReplayableEvent:
    event_id: str
    event_type: str
    payload: dict
    original_status: int
    original_at: datetime
    webhook_url: str

@dataclass
class ReplayResult:
    replay_id: str
    event_id: str
    original_status: int
    replay_status: int
    diff_detected: bool
    replayed_at: datetime
    latency_ms: float = 0.0

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiWebhookEventReplay:
    def __init__(self, max_stored: int = 5000) -> None:
        self._events: dict[tuple[str, str, str], ReplayableEvent] = {}  # (inst, consumer, event_id)
        self._replays: dict[tuple[str, str], list[ReplayResult]] = {}
        self._max = max_stored

    def store_event(self, installation_id: str, consumer_id: str, event: ReplayableEvent) -> ReplayableEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not event.webhook_url.startswith("https://"):
            raise ValueError("webhook_url must use HTTPS")
        self._events[(installation_id, consumer_id, event.event_id)] = event
        return event

    def replay(self, installation_id: str, consumer_id: str, event_id: str, now: datetime) -> ReplayResult:
        key = (installation_id, consumer_id, event_id)
        event = self._events.get(key)
        if not event:
            raise ValueError("Event not found")
        # Simulated replay
        result = ReplayResult(replay_id=f"rp-{now.isoformat()}", event_id=event_id, original_status=event.original_status, replay_status=event.original_status, diff_detected=False, replayed_at=now, latency_ms=25.0)
        rkey = (installation_id, consumer_id)
        if rkey not in self._replays:
            self._replays[rkey] = []
        self._replays[rkey].append(result)
        return result

    def replay_batch(self, installation_id: str, consumer_id: str, event_ids: list[str], now: datetime) -> list[ReplayResult]:
        results = []
        for eid in event_ids:
            try:
                results.append(self.replay(installation_id, consumer_id, eid, now))
            except ValueError:
                pass
        return results

    def get_stored_events(self, installation_id: str, consumer_id: str, event_type: str | None = None, limit: int = 20) -> list[ReplayableEvent]:
        events = [e for (inst, cid, _), e in self._events.items() if inst == installation_id and cid == consumer_id]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return sorted(events, key=lambda e: e.original_at, reverse=True)[:limit]

    def get_replay_history(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[ReplayResult]:
        return list(reversed(self._replays.get((installation_id, consumer_id), [])[-limit:]))
