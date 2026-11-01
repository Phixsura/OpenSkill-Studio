"""User segments — group users for targeted features and communications."""


def create_segment(*, name: str, rules: list[dict]) -> dict:
    if not name or len(name) < 2:
        return {"error": "Segment name too short"}
    if not rules:
        return {"error": "At least one rule required"}
    return {"name": name, "rules": rules, "status": "active", "error": None}


def evaluate_user(*, user: dict, rules: list[dict]) -> bool:
    for rule in rules:
        field = rule.get("field", "")
        op = rule.get("operator", "eq")
        value = rule.get("value")
        user_val = user.get(field)
        if op == "eq" and user_val != value:
            return False
        elif op == "gt" and (user_val is None or user_val <= value):
            return False
        elif op == "lt" and (user_val is None or user_val >= value):
            return False
        elif op == "in" and user_val not in (value or []):
            return False
    return True


def segment_users(*, users: list[dict], rules: list[dict]) -> dict:
    matched = [u for u in users if evaluate_user(user=u, rules=rules)]
    return {"matched": len(matched), "total": len(users),
            "match_rate": round(len(matched) / max(len(users), 1) * 100, 1)}
