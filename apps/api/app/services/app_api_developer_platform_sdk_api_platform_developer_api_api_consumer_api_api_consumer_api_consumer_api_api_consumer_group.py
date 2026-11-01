"""Consumer API Consumer Group — group consumers for shared policies."""
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
    policies: dict[str, str] = field(default_factory=dict)  # policy_type -> policy_id

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerGroup:
    def __init__(self) -> None:
        self._groups: dict[tuple[str, str], ConsumerGroup] = {}

    def create_group(self, installation_id: str, group: ConsumerGroup) -> ConsumerGroup:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not group.name:
            raise ValueError("name is required")
        key = (installation_id, group.group_id)
        if key in self._groups:
            raise ValueError(f"Group {group.group_id} already exists")
        self._groups[key] = group
        return group

    def add_member(self, installation_id: str, group_id: str, consumer_id: str) -> ConsumerGroup:
        key = (installation_id, group_id)
        group = self._groups.get(key)
        if not group:
            raise ValueError("Group not found")
        if consumer_id in group.members:
            raise ValueError("Consumer already in group")
        group.members.append(consumer_id)
        return group

    def remove_member(self, installation_id: str, group_id: str, consumer_id: str) -> ConsumerGroup:
        key = (installation_id, group_id)
        group = self._groups.get(key)
        if not group:
            raise ValueError("Group not found")
        if consumer_id not in group.members:
            raise ValueError("Consumer not in group")
        group.members.remove(consumer_id)
        return group

    def get_consumer_groups(self, installation_id: str, consumer_id: str) -> list[ConsumerGroup]:
        return [g for (inst, _), g in self._groups.items() if inst == installation_id and consumer_id in g.members]

    def set_policy(self, installation_id: str, group_id: str, policy_type: str, policy_id: str) -> ConsumerGroup:
        key = (installation_id, group_id)
        group = self._groups.get(key)
        if not group:
            raise ValueError("Group not found")
        group.policies[policy_type] = policy_id
        return group

    def list_groups(self, installation_id: str) -> list[ConsumerGroup]:
        return sorted([g for (inst, _), g in self._groups.items() if inst == installation_id], key=lambda g: g.name)
