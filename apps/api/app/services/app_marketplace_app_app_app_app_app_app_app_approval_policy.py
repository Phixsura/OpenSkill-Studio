"""Deployment approval policy — enforce approval policies based on risk."""
from __future__ import annotations


def evaluate_approval(deployment: dict, policies: list[dict]) -> dict:
    required_approvers = set()
    matched_policies = []
    for policy in policies:
        match = True
        for cond in policy.get("conditions", []):
            field = cond["field"]
            value = deployment.get(field)
            if cond["op"] == "eq" and value != cond["value"]:
                match = False
            elif cond["op"] == "gt" and (value is None or value <= cond["value"]):
                match = False
        if match:
            matched_policies.append(policy["name"])
            required_approvers.update(policy.get("approvers", []))
    auto_approve = len(required_approvers) == 0
    return {"requires_approval": not auto_approve,
            "required_approvers": sorted(required_approvers),
            "matched_policies": matched_policies,
            "auto_approve": auto_approve}
