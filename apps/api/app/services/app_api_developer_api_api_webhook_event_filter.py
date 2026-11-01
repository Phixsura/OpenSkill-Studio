"""App API Developer Webhook Event Filter — filter events before delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class EventFilter:
    filter_id: str
    destination: str
    include_events: list[str] = field(default_factory=list)
    exclude_events: list[str] = field(default_factory=list)
    field_filters: dict[str, str] = field(default_factory=dict)  # field -> regex pattern
    matched_count: int = 0
    dropped_count: int = 0

class AppAPIDeveloperAPIApiWebhookEventFilter:
    def __init__(self) -> None:
        self._filters: dict[tuple[str, str], EventFilter] = {}

    def create(self, installation_id: str, filter_id: str, destination: str, include_events: list[str] | None = None, exclude_events: list[str] | None = None, field_filters: dict[str, str] | None = None) -> EventFilter:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, filter_id)
        if key in self._filters: raise ValueError(f"Filter {filter_id} exists")
        # Validate regex patterns
        for pattern in (field_filters or {}).values():
            re.compile(pattern)
        f = EventFilter(filter_id=filter_id, destination=destination, include_events=include_events or [], exclude_events=exclude_events or [], field_filters=field_filters or {})
        self._filters[key] = f
        return f

    def should_deliver(self, installation_id: str, filter_id: str, event_type: str, payload: dict) -> bool:
        f = self._get(installation_id, filter_id)
        if f.exclude_events and event_type in f.exclude_events:
            f.dropped_count += 1
            return False
        if f.include_events and event_type not in f.include_events:
            f.dropped_count += 1
            return False
        for field_name, pattern in f.field_filters.items():
            val = str(payload.get(field_name, ""))
            if not re.search(pattern, val):
                f.dropped_count += 1
                return False
        f.matched_count += 1
        return True

    def stats(self, installation_id: str, filter_id: str) -> dict[str, int]:
        f = self._get(installation_id, filter_id)
        return {"matched": f.matched_count, "dropped": f.dropped_count}

    def list_filters(self, installation_id: str) -> list[EventFilter]:
        return [f for (inst, _), f in self._filters.items() if inst == installation_id]

    def _get(self, installation_id: str, filter_id: str) -> EventFilter:
        key = (installation_id, filter_id)
        f = self._filters.get(key)
        if f is None: raise KeyError(f"Filter {filter_id} not found")
        return f
