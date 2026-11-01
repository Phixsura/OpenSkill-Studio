"""Webhook filter — conditional delivery based on payload content."""


def create_filter(*, name: str, conditions: list[dict]) -> dict:
    if not conditions:
        return {"error": "At least one condition required"}
    return {"name": name, "conditions": conditions, "status": "active", "error": None}


def evaluate_filter(*, payload: dict, conditions: list[dict], mode: str = "all") -> bool:
    results = []
    for cond in conditions:
        field = cond.get("field", "")
        op = cond.get("operator", "eq")
        value = cond.get("value")
        actual = payload
        for key in field.split("."):
            actual = actual.get(key) if isinstance(actual, dict) else None
        if op == "eq":
            results.append(actual == value)
        elif op == "ne":
            results.append(actual != value)
        elif op == "contains":
            results.append(value in str(actual) if actual else False)
        elif op == "exists":
            results.append(actual is not None)
        else:
            results.append(False)
    return all(results) if mode == "all" else any(results)
