"""Consumer API Token Revocation Log — track all token revocation events."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class RevocationEvent:
    event_id: str
    token_id: str
    consumer_id: str
    reason: str  # "manual", "rotation", "compromise", "expiry", "policy"
    revoked_by: str
    ip_address: str = ""
    timestamp: datetime | None = None

@dataclass
class RevocationSummary:
    total_revocations: int
    by_reason: dict[str, int]
    most_recent: RevocationEvent | None = None

VALID_REASONS = {"manual", "rotation", "compromise", "expiry", "policy", "abuse"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiTokenRevocationLog:
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], list[RevocationEvent]] = {}

    def record(self, installation_id: str, event: RevocationEvent) -> RevocationEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if event.reason not in VALID_REASONS:
            raise ValueError(f"Invalid reason: {event.reason}")
        event.timestamp = event.timestamp or datetime.utcnow()
        key = (installation_id, event.consumer_id)
        if key not in self._events:
            self._events[key] = []
        self._events[key].append(event)
        log.info("token_revoked", installation_id=installation_id, token=event.token_id, reason=event.reason)
        return event

    def get_summary(self, installation_id: str, consumer_id: str) -> RevocationSummary:
        events = self._events.get((installation_id, consumer_id), [])
        by_reason: dict[str, int] = {}
        for e in events:
            by_reason[e.reason] = by_reason.get(e.reason, 0) + 1
        return RevocationSummary(total_revocations=len(events), by_reason=by_reason, most_recent=events[-1] if events else None)

    def get_token_history(self, installation_id: str, consumer_id: str, token_id: str) -> list[RevocationEvent]:
        return [e for e in self._events.get((installation_id, consumer_id), []) if e.token_id == token_id]

    def list_recent(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[RevocationEvent]:
        return list(reversed(self._events.get((installation_id, consumer_id), [])[-limit:]))
