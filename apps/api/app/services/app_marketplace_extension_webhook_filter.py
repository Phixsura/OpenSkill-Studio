"""Extension Webhook Filter — filter webhook events before delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import re


@dataclass
class WebhookFilter:
    filter_id: str
    event_types: list[str] = field(default_factory=list)  # empty = all
    conditions: list[dict] = field(default_factory=list)  # [{field, op, value}]


class ExtWebhookFilterService:
    def __init__(self):
        self._filters: dict[str, WebhookFilter] = {}
        self._counter = 0

    def create(self, event_types: list[str] | None = None,
               conditions: list[dict] | None = None) -> WebhookFilter:
        self._counter += 1
        f = WebhookFilter(filter_id=f"wf-{self._counter}",
                          event_types=event_types or [],
                          conditions=conditions or [])
        self._filters[f.filter_id] = f
        return f

    def matches(self, filter_id: str, event_type: str, payload: dict) -> bool:
        f = self._filters.get(filter_id)
        if not f: return True
        if f.event_types and event_type not in f.event_types:
            return False
        for cond in f.conditions:
            val = payload.get(cond.get("field", ""))
            op = cond.get("op", "eq")
            expected = cond.get("value")
            if op == "eq" and val != expected: return False
            if op == "ne" and val == expected: return False
            if op == "gt" and (not isinstance(val, (int, float)) or val <= expected): return False
            if op == "contains" and (not isinstance(val, str) or expected not in val): return False
        return True

    def get(self, filter_id: str) -> WebhookFilter | None:
        return self._filters.get(filter_id)
