"""App API Consumer Group — organize API consumers into groups.

Manages consumer groups:
- Create groups with shared settings
- Add/remove members
- Group-level rate limits
- Per-installation scoped groups
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ConsumerGroup:
    """A group of API consumers."""

    group_id: str
    name: str
    members: set[str] = field(default_factory=set)
    rate_limit: int = 0  # 0 = no group limit
    description: str = ""

    @property
    def member_count(self) -> int:
        return len(self.members)


class AppAPIConsumerGroup:
    """Organize API consumers into groups."""

    def __init__(self) -> None:
        self._groups: dict[tuple[str, str], ConsumerGroup] = {}

    def create_group(
        self, installation_id: str, group_id: str, name: str,
        rate_limit: int = 0, description: str = "",
    ) -> ConsumerGroup:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, group_id)
        if key in self._groups:
            raise ValueError(f"Group {group_id} already exists")

        group = ConsumerGroup(
            group_id=group_id, name=name,
            rate_limit=rate_limit, description=description,
        )
        self._groups[key] = group
        return group

    def add_member(self, installation_id: str, group_id: str, consumer_id: str) -> ConsumerGroup:
        g = self._get(installation_id, group_id)
        g.members.add(consumer_id)
        return g

    def remove_member(self, installation_id: str, group_id: str, consumer_id: str) -> ConsumerGroup:
        g = self._get(installation_id, group_id)
        g.members.discard(consumer_id)
        return g

    def find_groups(self, installation_id: str, consumer_id: str) -> list[ConsumerGroup]:
        return [
            g for (inst, _), g in self._groups.items()
            if inst == installation_id and consumer_id in g.members
        ]

    def list_groups(self, installation_id: str) -> list[ConsumerGroup]:
        return [g for (inst, _), g in self._groups.items() if inst == installation_id]

    def _get(self, installation_id: str, group_id: str) -> ConsumerGroup:
        key = (installation_id, group_id)
        g = self._groups.get(key)
        if g is None:
            raise KeyError(f"Group {group_id} not found")
        return g
