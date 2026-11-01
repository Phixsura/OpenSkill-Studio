"""Webhook Event Replay — replay failed or missed webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class WebhookEvent:
    event_id: str
    endpoint_url: str
    payload: dict
    status: str = "delivered"  # delivered, failed, pending, replayed
    attempts: int = 1
    last_attempt: float = 0.0
    response_code: int = 0
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()
        if not self.last_attempt: self.last_attempt = self.created_at


class WebhookReplayService:
    MAX_RETRIES = 5

    def __init__(self):
        self._events: dict[str, WebhookEvent] = {}
        self._counter = 0

    def record(self, endpoint_url: str, payload: dict, status: str = "delivered",
               response_code: int = 200) -> WebhookEvent:
        self._counter += 1
        evt = WebhookEvent(event_id=f"wh-{self._counter}", endpoint_url=endpoint_url,
                           payload=payload, status=status, response_code=response_code)
        self._events[evt.event_id] = evt
        return evt

    def replay(self, event_id: str) -> tuple[bool, str]:
        evt = self._events.get(event_id)
        if not evt:
            return False, "Event not found"
        if evt.attempts >= self.MAX_RETRIES:
            return False, f"Max retries ({self.MAX_RETRIES}) reached"
        evt.attempts += 1
        evt.last_attempt = time.time()
        evt.status = "replayed"
        return True, "Replay queued"

    def get_failed(self, limit: int = 50) -> list[WebhookEvent]:
        return [e for e in self._events.values()
                if e.status == "failed"][:limit]

    def get_history(self, endpoint_url: str | None = None,
                    limit: int = 100) -> list[WebhookEvent]:
        events = list(self._events.values())
        if endpoint_url:
            events = [e for e in events if e.endpoint_url == endpoint_url]
        return sorted(events, key=lambda e: e.created_at, reverse=True)[:limit]

    def get_stats(self) -> dict[str, int]:
        stats: dict[str, int] = {}
        for e in self._events.values():
            stats[e.status] = stats.get(e.status, 0) + 1
        return stats
