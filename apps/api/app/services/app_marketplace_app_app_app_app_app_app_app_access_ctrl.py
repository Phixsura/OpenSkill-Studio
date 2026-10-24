"""Platform access control — RBAC with fine-grained permissions."""
from __future__ import annotations


class AccessControl:
    def __init__(self):
        self._roles: dict[str, set[str]] = {}
        self._user_roles: dict[str, set[str]] = {}

    def define_role(self, role: str, permissions: list[str]) -> dict:
        self._roles[role] = set(permissions)
        return {"role": role, "permissions": sorted(permissions)}

    def assign_role(self, user_id: str, role: str) -> dict:
        self._user_roles.setdefault(user_id, set()).add(role)
        return {"user_id": user_id, "roles": sorted(self._user_roles[user_id])}

    def revoke_role(self, user_id: str, role: str) -> dict:
        self._user_roles.get(user_id, set()).discard(role)
        return {"user_id": user_id, "roles": sorted(self._user_roles.get(user_id, set()))}

    def check(self, user_id: str, permission: str) -> dict:
        roles = self._user_roles.get(user_id, set())
        for role in roles:
            if permission in self._roles.get(role, set()):
                return {"allowed": True, "user_id": user_id, "permission": permission,
                        "granted_by": role}
        return {"allowed": False, "user_id": user_id, "permission": permission}

    def user_permissions(self, user_id: str) -> dict:
        roles = self._user_roles.get(user_id, set())
        perms = set()
        for role in roles:
            perms.update(self._roles.get(role, set()))
        return {"user_id": user_id, "roles": sorted(roles),
                "permissions": sorted(perms), "count": len(perms)}

    def stats(self) -> dict:
        return {"roles": len(self._roles), "users_with_roles": len(self._user_roles),
                "total_permissions": sum(len(p) for p in self._roles.values())}
