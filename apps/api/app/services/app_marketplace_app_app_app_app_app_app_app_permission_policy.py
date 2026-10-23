"""Permission policy engine — ABAC-style policy evaluation."""
from __future__ import annotations


class PermissionPolicyEngine:
    def __init__(self):
        self._policies: list[dict] = []

    def add_policy(self, *, name: str, effect: str, resource: str,
                    actions: list[str], conditions: dict | None = None) -> dict:
        if effect not in ("allow", "deny"):
            return {"error": "Effect must be 'allow' or 'deny'"}
        policy = {"name": name, "effect": effect, "resource": resource,
                  "actions": actions, "conditions": conditions or {}}
        self._policies.append(policy)
        return {"added": name, "effect": effect}

    def evaluate(self, *, resource: str, action: str, context: dict | None = None) -> dict:
        ctx = context or {}
        matched = []
        for p in self._policies:
            if not self._resource_match(p["resource"], resource):
                continue
            if action not in p["actions"] and "*" not in p["actions"]:
                continue
            if not self._conditions_met(p["conditions"], ctx):
                continue
            matched.append(p)
        # Deny takes precedence
        for p in matched:
            if p["effect"] == "deny":
                return {"allowed": False, "reason": "denied", "policy": p["name"]}
        for p in matched:
            if p["effect"] == "allow":
                return {"allowed": True, "reason": "allowed", "policy": p["name"]}
        return {"allowed": False, "reason": "no_matching_policy"}

    @staticmethod
    def _resource_match(pattern: str, resource: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith("/*"):
            return resource.startswith(pattern[:-1])
        return pattern == resource

    @staticmethod
    def _conditions_met(conditions: dict, context: dict) -> bool:
        for key, expected in conditions.items():
            if context.get(key) != expected:
                return False
        return True
