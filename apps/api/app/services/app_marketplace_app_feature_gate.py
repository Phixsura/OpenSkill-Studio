"""Feature gate — control feature access by plan, role, or org."""


GATE_TYPES = {"plan", "role", "org", "user", "percentage"}


def evaluate_gate(*, gate: dict, context: dict) -> dict:
    gate_type = gate.get("type")
    if gate_type not in GATE_TYPES:
        return {"allowed": False, "error": f"Unknown gate type: {gate_type}"}

    if gate_type == "plan":
        allowed_plans = gate.get("plans", [])
        user_plan = context.get("plan", "free")
        return {"allowed": user_plan in allowed_plans,
                "reason": f"Plan '{user_plan}' {'in' if user_plan in allowed_plans else 'not in'} {allowed_plans}"}

    if gate_type == "role":
        allowed_roles = gate.get("roles", [])
        user_role = context.get("role", "viewer")
        return {"allowed": user_role in allowed_roles,
                "reason": f"Role '{user_role}' check"}

    if gate_type == "org":
        allowed_orgs = gate.get("org_ids", [])
        user_org = context.get("org_id", "")
        return {"allowed": user_org in allowed_orgs,
                "reason": f"Org '{user_org}' check"}

    if gate_type == "percentage":
        import hashlib
        pct = gate.get("percentage", 0)
        user_id = context.get("user_id", "")
        h = int(hashlib.sha256(f"{gate.get('feature')}:{user_id}".encode()).hexdigest(), 16) % 100
        return {"allowed": h < pct, "reason": f"Percentage rollout ({pct}%)"}

    return {"allowed": True, "reason": "User-level gate (always allowed for named users)"}


def check_feature_access(*, feature: str, gates: list[dict], context: dict) -> dict:
    if not gates:
        return {"feature": feature, "allowed": True, "reason": "No gates configured"}
    for gate in gates:
        result = evaluate_gate(gate=gate, context=context)
        if not result.get("allowed"):
            return {"feature": feature, "allowed": False, "blocked_by": gate.get("type"),
                    "reason": result.get("reason", "")}
    return {"feature": feature, "allowed": True, "reason": "All gates passed"}
