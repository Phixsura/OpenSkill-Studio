"""App Webhook Filter — filter and route webhooks by event patterns.

Manages webhook event filtering:
- Define filter rules with glob patterns
- Match events against filters
- Include/exclude mode
- Per-installation scoped filters
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class WebhookFilter:
    """A webhook event filter rule."""

    filter_id: str
    webhook_id: str
    patterns: list[str]  # glob patterns, e.g. "user.*", "order.created"
    mode: str = "include"  # "include" or "exclude"


class AppWebhookFilter:
    """Filter and route webhooks by event patterns."""

    def __init__(self) -> None:
        # (installation_id, filter_id) → WebhookFilter
        self._filters: dict[tuple[str, str], WebhookFilter] = {}

    def create_filter(
        self,
        installation_id: str,
        filter_id: str,
        webhook_id: str,
        patterns: list[str],
        mode: str = "include",
    ) -> WebhookFilter:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not filter_id:
            raise ValueError("filter_id is required")
        if not patterns:
            raise ValueError("at least one pattern is required")
        if mode not in ("include", "exclude"):
            raise ValueError("mode must be 'include' or 'exclude'")

        key = (installation_id, filter_id)
        if key in self._filters:
            raise ValueError(f"Filter {filter_id} already exists")

        f = WebhookFilter(
            filter_id=filter_id, webhook_id=webhook_id,
            patterns=patterns, mode=mode,
        )
        self._filters[key] = f
        return f

    def should_deliver(
        self, installation_id: str, webhook_id: str, event_type: str
    ) -> bool:
        """Check if an event should be delivered to a webhook."""
        filters = [
            f for (inst, _), f in self._filters.items()
            if inst == installation_id and f.webhook_id == webhook_id
        ]

        if not filters:
            return True  # no filters = deliver all

        for f in filters:
            matches = any(fnmatch.fnmatch(event_type, p) for p in f.patterns)
            if f.mode == "include" and matches:
                return True
            if f.mode == "exclude" and matches:
                return False

        # If only include filters exist and none matched → deny
        has_include = any(f.mode == "include" for f in filters)
        return not has_include

    def match_patterns(self, event_type: str, patterns: list[str]) -> bool:
        """Test if an event type matches any pattern."""
        return any(fnmatch.fnmatch(event_type, p) for p in patterns)

    def list_filters(self, installation_id: str, webhook_id: str | None = None) -> list[WebhookFilter]:
        filters = [f for (inst, _), f in self._filters.items() if inst == installation_id]
        if webhook_id:
            filters = [f for f in filters if f.webhook_id == webhook_id]
        return filters

    def remove_filter(self, installation_id: str, filter_id: str) -> bool:
        key = (installation_id, filter_id)
        if key in self._filters:
            del self._filters[key]
            return True
        return False
