"""Sandbox Access Policy — fine-grained access policies for sandbox resources.

Defines RBAC policies with roles, resource-level permissions, policy
inheritance, and access decision logging.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class Action(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass
class PolicyRule:
    resource: str  # e.g. "files:*", "env:*", "network:outbound"
    actions: list[Action]
    decision: Decision = Decision.ALLOW


@dataclass
class Role:
    name: str
    rules: list[PolicyRule] = field(default_factory=list)
    inherits: list[str] = field(default_factory=list)


class SandboxAccessPolicyService:
    """RBAC access policy engine for sandbox resources."""

    def __init__(self):
        self._roles: dict[str, Role] = {}
        self._assignments: dict[str, dict[str, str]] = defaultdict(dict)  # sandbox -> {user: role}

    def define_role(self, name: str, rules: list[dict],
                    inherits: list[str] | None = None) -> Role:
        parsed = [PolicyRule(
            resource=r["resource"],
            actions=[Action(a) for a in r["actions"]],
            decision=Decision(r.get("decision", "allow")),
        ) for r in rules]
        for parent in (inherits or []):
            if parent not in self._roles:
                raise ValueError(f"Parent role not found: {parent}")
        role = Role(name=name, rules=parsed, inherits=inherits or [])
        self._roles[name] = role
        return role

    def assign_role(self, sandbox_id: str, user_id: str, role_name: str) -> bool:
        if role_name not in self._roles:
            return False
        self._assignments[sandbox_id][user_id] = role_name
        return True

    def _get_effective_rules(self, role_name: str, visited: set[str] | None = None) -> list[PolicyRule]:
        visited = visited or set()
        if role_name in visited:
            return []  # prevent circular inheritance
        visited.add(role_name)
        role = self._roles.get(role_name)
        if not role:
            return []
        rules = list(role.rules)
        for parent in role.inherits:
            rules.extend(self._get_effective_rules(parent, visited))
        return rules

    def check_access(self, sandbox_id: str, user_id: str,
                     resource: str, action: Action) -> dict:
        role_name = self._assignments.get(sandbox_id, {}).get(user_id)
        if not role_name:
            return {"allowed": False, "reason": "No role assigned"}

        rules = self._get_effective_rules(role_name)
        # Check deny rules first
        for rule in rules:
            if rule.decision == Decision.DENY and self._matches(rule.resource, resource):
                if action in rule.actions:
                    return {"allowed": False, "reason": f"Denied by rule: {rule.resource}"}

        # Check allow rules
        for rule in rules:
            if rule.decision == Decision.ALLOW and self._matches(rule.resource, resource):
                if action in rule.actions:
                    return {"allowed": True, "role": role_name}

        return {"allowed": False, "reason": "No matching allow rule"}

    def _matches(self, pattern: str, resource: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith(":*"):
            prefix = pattern[:-1]
            return resource.startswith(prefix) or resource == pattern[:-2]
        return pattern == resource

    def get_user_role(self, sandbox_id: str, user_id: str) -> str | None:
        return self._assignments.get(sandbox_id, {}).get(user_id)

    def list_roles(self) -> list[dict]:
        return [{"name": r.name, "rule_count": len(r.rules),
                 "inherits": r.inherits}
                for r in self._roles.values()]
