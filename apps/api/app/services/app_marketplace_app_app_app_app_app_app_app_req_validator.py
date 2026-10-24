"""Platform request validator — validate incoming API requests."""
from __future__ import annotations
import re


def validate_request(request: dict, rules: dict) -> dict:
    errors = []
    for field, constraints in rules.items():
        value = request.get(field)
        if constraints.get("required") and value is None:
            errors.append({"field": field, "error": "required"})
            continue
        if value is None:
            continue
        if "type" in constraints:
            expected = constraints["type"]
            if expected == "string" and not isinstance(value, str):
                errors.append({"field": field, "error": f"expected string"})
            elif expected == "int" and not isinstance(value, int):
                errors.append({"field": field, "error": "expected int"})
        if "min_length" in constraints and isinstance(value, str) and len(value) < constraints["min_length"]:
            errors.append({"field": field, "error": f"min length {constraints['min_length']}"})
        if "max_length" in constraints and isinstance(value, str) and len(value) > constraints["max_length"]:
            errors.append({"field": field, "error": f"max length {constraints['max_length']}"})
        if "pattern" in constraints and isinstance(value, str):
            if not re.match(constraints["pattern"], value):
                errors.append({"field": field, "error": f"pattern mismatch"})
    return {"valid": len(errors) == 0, "errors": errors}


def sanitize_input(value: str, max_length: int = 1000) -> str:
    import html
    return html.escape(value[:max_length].strip())
