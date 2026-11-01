"""App API Developer Role — manage developer roles and permissions."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DeveloperRole:
    role_id: str
    name: str
    permissions: set[str] = field(default_factory=set)
    member_count: int = 0

class AppAPIDeveloperRole:
    def __init__(self) -> None:
        self._roles: dict[tuple[str, str], DeveloperRole] = {}
        self._assignments: dict[tuple[str, str], str] = {}

    def create_role(self, installation_id: str, role_id: str, name: str, permissions: list[str]) -> DeveloperRole:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, role_id)
        if key in self._roles: raise ValueError(f"Role {role_id} exists")
        r = DeveloperRole(role_id=role_id, name=name, permissions=set(permissions))
        self._roles[key] = r
        return r

    def assign(self, installation_id: str, developer_id: str, role_id: str) -> None:
        if (installation_id, role_id) not in self._roles: raise KeyError(f"Role {role_id} not found")
        self._assignments[(installation_id, developer_id)] = role_id
        self._roles[(installation_id, role_id)].member_count += 1

    def has_permission(self, installation_id: str, developer_id: str, permission: str) -> bool:
        rid = self._assignments.get((installation_id, developer_id))
        if rid is None: return False
        role = self._roles.get((installation_id, rid))
        return role is not None and permission in role.permissions

    def list_roles(self, installation_id: str) -> list[DeveloperRole]:
        return [r for (inst, _), r in self._roles.items() if inst == installation_id]
