"""App API Webhook Priority — prioritize webhook deliveries.

Manages webhook delivery priority:
- Assign priority levels to event types
- Higher priority = delivered first
- Track priority distribution
- Per-installation scoped priorities
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class EventPriority:
    """Priority configuration for an event type."""

    event_type: str
    priority: int  # 1=low, 5=critical
    delivery_count: int = 0


VALID_PRIORITIES = range(1, 6)


class AppAPIWebhookPriority:
    """Prioritize webhook deliveries."""

    def __init__(self) -> None:
        self._priorities: dict[tuple[str, str], EventPriority] = {}

    def set_priority(
        self, installation_id: str, event_type: str, priority: int,
    ) -> EventPriority:
        if not installation_id:
            raise ValueError("installation_id is required")
        if priority not in VALID_PRIORITIES:
            raise ValueError("priority must be 1-5")

        ep = EventPriority(event_type=event_type, priority=priority)
        self._priorities[(installation_id, event_type)] = ep
        return ep

    def get_priority(self, installation_id: str, event_type: str) -> int:
        ep = self._priorities.get((installation_id, event_type))
        return ep.priority if ep else 3  # default medium

    def record_delivery(self, installation_id: str, event_type: str) -> EventPriority:
        key = (installation_id, event_type)
        ep = self._priorities.get(key)
        if ep is None:
            raise KeyError(f"No priority for {event_type}")
        ep.delivery_count += 1
        return ep

    def sorted_by_priority(self, installation_id: str) -> list[EventPriority]:
        eps = [ep for (inst, _), ep in self._priorities.items() if inst == installation_id]
        return sorted(eps, key=lambda e: e.priority, reverse=True)

    def list_priorities(self, installation_id: str) -> list[EventPriority]:
        return [ep for (inst, _), ep in self._priorities.items() if inst == installation_id]
