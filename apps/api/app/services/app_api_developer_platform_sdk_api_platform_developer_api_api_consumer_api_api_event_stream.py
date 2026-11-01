"""API Consumer Event Stream — real-time event streaming via SSE/WebSocket."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class StreamEvent:
    event_id: str
    event_type: str
    data: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class StreamSubscription:
    subscription_id: str
    consumer_id: str
    event_types: list[str]  # filter by event type
    transport: str = "sse"  # "sse" or "websocket"
    active: bool = True
    events_delivered: int = 0

VALID_TRANSPORTS = {"sse", "websocket"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEventStream:
    def __init__(self) -> None:
        self._subscriptions: dict[tuple[str, str], StreamSubscription] = {}
        self._buffer: dict[str, list[StreamEvent]] = {}

    def subscribe(self, installation_id: str, sub: StreamSubscription) -> StreamSubscription:
        if not installation_id: raise ValueError("installation_id is required")
        if sub.transport not in VALID_TRANSPORTS: raise ValueError(f"Invalid transport: {sub.transport}")
        if not sub.event_types: raise ValueError("At least one event type required")
        key = (installation_id, sub.subscription_id)
        if key in self._subscriptions: raise ValueError(f"Subscription {sub.subscription_id} exists")
        self._subscriptions[key] = sub
        return sub

    def publish(self, installation_id: str, event: StreamEvent) -> int:
        """Publish event and return number of matching subscribers."""
        self._buffer.setdefault(installation_id, []).append(event)
        matched = 0
        for (inst, _), sub in self._subscriptions.items():
            if inst == installation_id and sub.active and event.event_type in sub.event_types:
                sub.events_delivered += 1
                matched += 1
        return matched

    def unsubscribe(self, installation_id: str, subscription_id: str) -> bool:
        key = (installation_id, subscription_id)
        if key in self._subscriptions: del self._subscriptions[key]; return True
        return False

    def active_subscriptions(self, installation_id: str) -> list[StreamSubscription]:
        return [s for (inst, _), s in self._subscriptions.items() if inst == installation_id and s.active]

    def list_subscriptions(self, installation_id: str) -> list[StreamSubscription]:
        return [s for (inst, _), s in self._subscriptions.items() if inst == installation_id]
