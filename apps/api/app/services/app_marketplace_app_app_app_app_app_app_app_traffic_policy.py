"""Traffic policy — define request routing and retry policies."""
from __future__ import annotations


def create_policy(name: str, rules: list[dict]) -> dict:
    items = []
    for r in rules:
        items.append({"match": r.get("match", "/*"), "action": r.get("action", "allow"),
                       "priority": r.get("priority", 100),
                       "rate_limit": r.get("rate_limit", 0),
                       "timeout_ms": r.get("timeout_ms", 30000)})
    items.sort(key=lambda x: x["priority"])
    return {"name": name, "rules": items, "rule_count": len(items)}


def evaluate_request(policy: dict, path: str) -> dict:
    for rule in policy["rules"]:
        pattern = rule["match"]
        if pattern == "/*" or path.startswith(pattern.rstrip("*")):
            return {"matched": True, "rule": rule, "action": rule["action"]}
    return {"matched": False, "action": "allow"}  # default allow


def policy_stats(policies: list[dict]) -> dict:
    total_rules = sum(p["rule_count"] for p in policies)
    return {"total_policies": len(policies), "total_rules": total_rules,
            "avg_rules": round(total_rules / max(len(policies), 1), 1)}
