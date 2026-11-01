"""API Consumer Group — organize consumers into named groups with shared policies."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerGroup:
    group_id: str
    name: str
    description: str = ""
    members: list[str] = field(default_factory=list)
    policies: dict[str, str] = field(default_factory=dict)  # policy_type → policy_id
    max_members: int = 100

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGroup:
    def __init__(self) -> None:
        self._groups: dict[tuple[str, str], ConsumerGroup] = {}

    def create_group(self, installation_id: str, group: ConsumerGroup) -> ConsumerGroup:
        if not installation_id: raise ValueError("installation_id is required")
        if not group.name: raise ValueError("name is required")
        if group.max_members < 1: raise ValueError("max_members must be >= 1")
        key = (installation_id, group.group_id)
        if key in self._groups: raise ValueError(f"Group {group.group_id} already exists")
        self._groups[key] = group
        return group

    def add_member(self, installation_id: str, group_id: str, consumer_id: str) -> ConsumerGroup:
        g = self._get(installation_id, group_id)
        if consumer_id in g.members: raise ValueError(f"{consumer_id} already in group")
        if len(g.members) >= g.max_members: raise ValueError("Group is full")
        g.members.append(consumer_id)
        return g

    def remove_member(self, installation_id: str, group_id: str, consumer_id: str) -> ConsumerGroup:
        g = self._get(installation_id, group_id)
        if consumer_id not in g.members: raise KeyError(f"{consumer_id} not in group")
        g.members.remove(consumer_id)
        return g

    def groups_for_consumer(self, installation_id: str, consumer_id: str) -> list[ConsumerGroup]:
        return [g for (inst, _), g in self._groups.items() if inst == installation_id and consumer_id in g.members]

    def set_policy(self, installation_id: str, group_id: str, policy_type: str, policy_id: str) -> ConsumerGroup:
        g = self._get(installation_id, group_id)
        g.policies[policy_type] = policy_id
        return g

    def list_groups(self, installation_id: str) -> list[ConsumerGroup]:
        return [g for (inst, _), g in self._groups.items() if inst == installation_id]

    def _get(self, installation_id: str, group_id: str) -> ConsumerGroup:
        g = self._groups.get((installation_id, group_id))
        if g is None: raise KeyError(f"Group {group_id} not found")
        return g
