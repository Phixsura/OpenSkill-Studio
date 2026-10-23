"""Webhook filter — filter webhook events before delivery."""

import re


def create_filter(*, name: str, conditions: list[dict]) -> dict:
    if not conditions:
        return {"error": "At least one condition required"}
    validated = []
    for cond in conditions:
        field = cond.get("field", "")
        operator = cond.get("operator", "eq")
        value = cond.get("value")
        valid_ops = {"eq", "ne", "contains", "starts_with", "gt", "lt", "in", "exists"}
        if operator not in valid_ops:
            return {"error": f"Invalid operator: {operator}"}
        validated.append({"field": field, "operator": operator, "value": value})
    return {"name": name, "conditions": validated, "condition_count": len(validated), "active": True}


def apply_filter(*, event: dict, conditions: list[dict]) -> dict:
    for cond in conditions:
        field = cond["field"]
        value = event
        for part in field.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        op = cond["operator"]
        target = cond["value"]
        match = False
        if op == "eq":
            match = value == target
        elif op == "ne":
            match = value != target
        elif op == "contains" and isinstance(value, str):
            match = target in value
        elif op == "starts_with" and isinstance(value, str):
            match = value.startswith(str(target))
        elif op == "exists":
            match = value is not None
        elif op == "gt" and isinstance(value, (int, float)):
            match = value > target
        elif op == "lt" and isinstance(value, (int, float)):
            match = value < target
        elif op == "in" and isinstance(target, list):
            match = value in target
        if not match:
            return {"deliver": False, "blocked_by": cond["field"]}
    return {"deliver": True}
