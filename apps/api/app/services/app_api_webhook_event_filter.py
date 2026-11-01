"""App API Webhook Event Filter — filter events by field conditions."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EventFilter:
    filter_id: str
    event_type: str
    field_path: str
    operator: str  # "eq", "ne", "contains", "gt", "lt"
    value: str
    enabled: bool = True

VALID_OPS = {"eq", "ne", "contains", "gt", "lt"}

class AppAPIWebhookEventFilter:
    def __init__(self) -> None:
        self._filters: dict[tuple[str, str], EventFilter] = {}

    def add_filter(self, installation_id: str, filter_id: str, event_type: str, field_path: str, operator: str, value: str) -> EventFilter:
        if not installation_id: raise ValueError("installation_id is required")
        if operator not in VALID_OPS: raise ValueError(f"operator must be one of {VALID_OPS}")
        f = EventFilter(filter_id=filter_id, event_type=event_type, field_path=field_path, operator=operator, value=value)
        self._filters[(installation_id, filter_id)] = f
        return f

    def matches(self, installation_id: str, event_type: str, payload: dict) -> bool:
        """Check if event passes all filters (AND logic). Returns True if should deliver."""
        filters = [f for (inst, _), f in self._filters.items() if inst == installation_id and f.enabled and f.event_type == event_type]
        if not filters: return True
        for f in filters:
            val = self._resolve(payload, f.field_path)
            if val is None: return False
            str_val = str(val)
            if f.operator == "eq" and str_val != f.value: return False
            if f.operator == "ne" and str_val == f.value: return False
            if f.operator == "contains" and f.value not in str_val: return False
        return True

    def list_filters(self, installation_id: str) -> list[EventFilter]:
        return [f for (inst, _), f in self._filters.items() if inst == installation_id]

    def _resolve(self, payload: dict, path: str) -> object | None:
        current: object = payload
        for part in path.split("."):
            if isinstance(current, dict) and part in current: current = current[part]
            else: return None
        return current
