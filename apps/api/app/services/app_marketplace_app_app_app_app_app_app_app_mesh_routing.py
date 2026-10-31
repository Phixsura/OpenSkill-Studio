"""Service mesh routing — define and evaluate routing rules."""
from __future__ import annotations


def evaluate_route(request: dict, rules: list[dict]) -> dict:
    for rule in rules:
        match = True
        for cond in rule.get("conditions", []):
            field = cond["field"]
            op = cond["op"]
            val = cond["value"]
            actual = request.get(field, "")
            if op == "eq" and actual != val:
                match = False
            elif op == "prefix" and not str(actual).startswith(str(val)):
                match = False
            elif op == "contains" and str(val) not in str(actual):
                match = False
            elif op == "header" and val not in request.get("headers", {}):
                match = False
        if match:
            return {"matched": True, "rule": rule["name"],
                    "destination": rule["destination"],
                    "weight": rule.get("weight", 100)}
    return {"matched": False, "rule": None, "destination": "default", "weight": 100}


def weighted_split(destinations: list[dict]) -> dict:
    total = sum(d["weight"] for d in destinations)
    normalized = []
    for d in destinations:
        normalized.append({"destination": d["destination"],
                           "weight": d["weight"],
                           "pct": round(d["weight"] / max(total, 1) * 100, 1)})
    return {"destinations": normalized, "total_weight": total}
