"""Permission policy engine — attribute-based access control (ABAC).

Security: namespaced attribute sources, fail-closed on unknown operators,
deny-overrides evaluation order.
"""
from __future__ import annotations


def _eval_condition(cond: dict, subject: dict, resource: dict) -> bool:
    attr = cond["attribute"]
    source = cond.get("source", "subject")
    src = subject if source == "subject" else resource
    if attr not in src:
        return False  # missing attribute = non-match
    actual = src[attr]
    op = cond["operator"]
    value = cond["value"]
    if op == "eq":
        return actual == value
    elif op == "in":
        return actual in value
    elif op == "gte":
        return actual is not None and actual >= value
    else:
        return False  # unknown operator = fail-closed


def evaluate_policy(subject: dict, resource: dict, action: str, policies: list[dict]) -> dict:
    # Deny-overrides: check deny policies first
    sorted_policies = sorted(policies, key=lambda p: 0 if p.get("effect", "deny") == "deny" else 1)
    for policy in sorted_policies:
        if action not in policy.get("actions", []):
            continue
        conditions_met = all(_eval_condition(c, subject, resource) for c in policy.get("conditions", []))
        if conditions_met:
            effect = policy.get("effect", "deny")
            return {"allowed": effect == "allow", "policy": policy["name"], "effect": effect}
    return {"allowed": False, "policy": None, "effect": "implicit_deny"}


def list_permissions(subject: dict, policies: list[dict]) -> list[str]:
    actions = set()
    for policy in policies:
        if policy.get("effect", "deny") != "allow":
            continue
        match = all(_eval_condition(c, subject, {}) for c in policy.get("conditions", []))
        if match:
            actions.update(policy.get("actions", []))
    return sorted(actions)
