"""Extension Access Control List — fine-grained ACL for extension resources."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AclRule:
    resource: str
    principal: str  # user_id, role:admin, group:devs
    permissions: set[str] = field(default_factory=set)  # read, write, delete, admin


class ExtAclService:
    VALID_PERMS = frozenset(["read", "write", "delete", "admin", "execute"])

    def __init__(self):
        self._rules: dict[str, list[AclRule]] = {}  # ext_id -> rules

    def grant(self, extension_id: str, resource: str, principal: str,
              permissions: list[str]) -> AclRule:
        perms = {p for p in permissions if p in self.VALID_PERMS}
        if not perms:
            raise ValueError("No valid permissions")
        rule = AclRule(resource=resource, principal=principal, permissions=perms)
        if extension_id not in self._rules:
            self._rules[extension_id] = []
        # Replace existing rule for same resource+principal
        self._rules[extension_id] = [
            r for r in self._rules[extension_id]
            if not (r.resource == resource and r.principal == principal)
        ]
        self._rules[extension_id].append(rule)
        return rule

    def check(self, extension_id: str, resource: str, principal: str,
              permission: str) -> bool:
        rules = self._rules.get(extension_id, [])
        for r in rules:
            if r.resource == resource and r.principal == principal:
                if permission in r.permissions or "admin" in r.permissions:
                    return True
        return False

    def revoke(self, extension_id: str, resource: str, principal: str) -> bool:
        rules = self._rules.get(extension_id, [])
        before = len(rules)
        self._rules[extension_id] = [
            r for r in rules if not (r.resource == resource and r.principal == principal)
        ]
        return len(self._rules[extension_id]) < before

    def get_rules(self, extension_id: str) -> list[AclRule]:
        return self._rules.get(extension_id, [])
