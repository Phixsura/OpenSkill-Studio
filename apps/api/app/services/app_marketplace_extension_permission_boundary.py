"""Permission Boundary — upper bound on grantable permissions.

AWS IAM-style permission boundaries: even if a role grants a permission,
the boundary constrains what's actually effective.

Implements:
- Define maximum permission sets (boundaries)
- Effective permissions = intersection(granted, boundary)
- Boundary inheritance (child can't exceed parent)
- Boundary violation detection
- Policy simulation (what-if with different boundaries)
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PermissionSet:
    name: str
    permissions: set[str] = field(default_factory=set)

    def allows(self, permission: str) -> bool:
        if "*" in self.permissions:
            return True
        # Check wildcard prefix: "read:*" matches "read:users"
        for p in self.permissions:
            if p.endswith(":*"):
                prefix = p[:-1]  # "read:"
                if permission.startswith(prefix):
                    return True
            if p == permission:
                return True
        return False


class PermissionBoundaryService:
    def __init__(self):
        self._boundaries: dict[str, PermissionSet] = {}
        self._grants: dict[str, PermissionSet] = {}  # entity -> granted
        self._entity_boundary: dict[str, str] = {}  # entity -> boundary name
        self._parent: dict[str, str] = {}  # boundary -> parent boundary

    def define_boundary(self, name: str, permissions: list[str],
                        parent: str = "") -> PermissionSet:
        if parent and parent not in self._boundaries:
            raise ValueError(f"Parent boundary '{parent}' not found")
        if parent:
            parent_boundary = self._boundaries[parent]
            # Child can't exceed parent
            violations = [p for p in permissions if not parent_boundary.allows(p)]
            if violations:
                raise ValueError(f"Boundary exceeds parent: {violations}")
            self._parent[name] = parent

        boundary = PermissionSet(name=name, permissions=set(permissions))
        self._boundaries[name] = boundary
        return boundary

    def assign_boundary(self, entity_id: str, boundary_name: str) -> bool:
        if boundary_name not in self._boundaries:
            return False
        self._entity_boundary[entity_id] = boundary_name
        return True

    def grant(self, entity_id: str, permissions: list[str]) -> PermissionSet:
        if entity_id not in self._grants:
            self._grants[entity_id] = PermissionSet(name=f"grants:{entity_id}")
        self._grants[entity_id].permissions.update(permissions)
        return self._grants[entity_id]

    def effective_permissions(self, entity_id: str) -> set[str]:
        """Effective = intersection of granted permissions and boundary."""
        granted = self._grants.get(entity_id)
        if not granted:
            return set()

        boundary_name = self._entity_boundary.get(entity_id)
        if not boundary_name:
            return set(granted.permissions)  # no boundary = all granted

        boundary = self._boundaries.get(boundary_name)
        if not boundary:
            return set(granted.permissions)

        return {p for p in granted.permissions if boundary.allows(p)}

    def check(self, entity_id: str, permission: str) -> bool:
        return permission in self.effective_permissions(entity_id)

    def detect_violations(self, entity_id: str) -> list[str]:
        """Find granted permissions that exceed the boundary."""
        granted = self._grants.get(entity_id)
        if not granted:
            return []

        boundary_name = self._entity_boundary.get(entity_id)
        if not boundary_name:
            return []

        boundary = self._boundaries.get(boundary_name)
        if not boundary:
            return []

        return [p for p in granted.permissions if not boundary.allows(p)]

    def simulate(self, entity_id: str, boundary_name: str) -> dict:
        """What-if: what would effective permissions be under a different boundary?"""
        granted = self._grants.get(entity_id)
        if not granted:
            return {"effective": [], "blocked": []}

        boundary = self._boundaries.get(boundary_name)
        if not boundary:
            return {"effective": sorted(granted.permissions), "blocked": []}

        effective = {p for p in granted.permissions if boundary.allows(p)}
        blocked = {p for p in granted.permissions if not boundary.allows(p)}
        return {"effective": sorted(effective), "blocked": sorted(blocked)}
