"""Policy Engine — Attribute-Based Access Control (ABAC) with policy evaluation.

Goes beyond RBAC: decisions based on attributes of subject, resource,
action, and environment (time, IP, etc).

Implements:
- Policy definition with target matching and conditions
- Effect: allow/deny with deny-override combining
- Attribute-based conditions on subject/resource/environment
- Policy sets with ordering
- Obligation actions on permit (e.g., "log access")
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Effect(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass
class PolicyCondition:
    category: str  # subject, resource, action, environment
    attribute: str
    operator: str  # eq, ne, in, not_in, gt, lt, matches, exists
    value: object


@dataclass
class Policy:
    policy_id: str
    name: str
    description: str = ""
    effect: Effect = Effect.ALLOW
    conditions: list[PolicyCondition] = field(default_factory=list)
    priority: int = 0  # higher = evaluated first
    obligations: list[str] = field(default_factory=list)  # actions on permit
    enabled: bool = True


@dataclass
class AccessRequest:
    subject: dict  # who: {user_id, role, department, clearance, ...}
    resource: dict  # what: {type, owner, classification, ...}
    action: str     # how: read, write, delete, ...
    environment: dict = field(default_factory=dict)  # when/where: {time, ip, ...}


@dataclass
class AccessDecision:
    effect: Effect
    matched_policy: str = ""
    obligations: list[str] = field(default_factory=list)
    reason: str = ""


class PolicyEngineService:
    def __init__(self, default_effect: Effect = Effect.DENY):
        self._policies: list[Policy] = []
        self._default = default_effect

    def add_policy(self, policy: Policy) -> None:
        self._policies.append(policy)
        self._policies.sort(key=lambda p: p.priority, reverse=True)

    def evaluate(self, request: AccessRequest) -> AccessDecision:
        """Evaluate access request against all policies. Deny-override combining."""
        applicable = []
        for policy in self._policies:
            if not policy.enabled:
                continue
            if self._matches(policy, request):
                applicable.append(policy)

        if not applicable:
            return AccessDecision(effect=self._default, reason="No matching policy")

        # Deny-override: any deny → deny
        for policy in applicable:
            if policy.effect == Effect.DENY:
                return AccessDecision(effect=Effect.DENY,
                                     matched_policy=policy.policy_id,
                                     reason=f"Denied by policy: {policy.name}")

        # All matching policies allow
        allow_policy = applicable[0]
        return AccessDecision(effect=Effect.ALLOW,
                              matched_policy=allow_policy.policy_id,
                              obligations=list(allow_policy.obligations),
                              reason=f"Allowed by policy: {allow_policy.name}")

    def _matches(self, policy: Policy, request: AccessRequest) -> bool:
        for cond in policy.conditions:
            actual = self._get_attribute(cond.category, cond.attribute, request)
            if not self._eval_condition(actual, cond.operator, cond.value):
                return False
        return True

    def _get_attribute(self, category: str, attribute: str,
                       request: AccessRequest) -> object:
        if category == "subject":
            return request.subject.get(attribute)
        elif category == "resource":
            return request.resource.get(attribute)
        elif category == "action":
            return request.action if attribute == "type" else None
        elif category == "environment":
            return request.environment.get(attribute)
        return None

    def _eval_condition(self, actual: object, operator: str, expected: object) -> bool:
        if operator == "exists":
            return actual is not None
        if actual is None:
            return operator == "ne"

        if operator == "eq": return actual == expected
        if operator == "ne": return actual != expected
        if operator == "in": return actual in expected
        if operator == "not_in": return actual not in expected
        if operator == "gt": return isinstance(actual, (int, float)) and actual > expected
        if operator == "lt": return isinstance(actual, (int, float)) and actual < expected
        if operator == "matches":
            import re
            return isinstance(actual, str) and bool(re.search(str(expected), actual))
        return False
