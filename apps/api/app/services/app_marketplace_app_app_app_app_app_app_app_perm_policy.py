"""Permission policy engine — attribute-based access control (ABAC)."""
from __future__ import annotations


def evaluate_policy(subject: dict, resource: dict, action: str, policies: list[dict]) -> dict:
    for policy in policies:
        if action not in policy.get("actions", []):
            continue
        conditions_met = True
        for cond in policy.get("conditions", []):
            attr = cond["attribute"]
            op = cond["operator"]
            value = cond["value"]
            actual = subject.get(attr) or resource.get(attr)
            if op == "eq" and actual != value:
                conditions_met = False
            elif op == "in" and actual not in value:
                conditions_met = False
            elif op == "gte" and (actual is None or actual < value):
                conditions_met = False
        if conditions_met:
            effect = policy.get("effect", "allow")
            return {"allowed": effect == "allow", "policy": policy["name"],
                    "effect": effect}
    return {"allowed": False, "policy": None, "effect": "implicit_deny"}


def list_permissions(subject: dict, policies: list[dict]) -> list[str]:
    actions = set()
    for policy in policies:
        if policy.get("effect", "allow") != "allow":
            continue
        match = True
        for cond in policy.get("conditions", []):
            actual = subject.get(cond["attribute"])
            if cond["operator"] == "eq" and actual != cond["value"]:
                match = False
            elif cond["operator"] == "in" and actual not in cond["value"]:
                match = False
        if match:
            actions.update(policy.get("actions", []))
    return sorted(actions)
