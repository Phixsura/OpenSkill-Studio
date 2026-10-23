"""Request validator — validate API request payloads."""
from __future__ import annotations
import re

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
URL_RE = re.compile(r"^https?://[^\s]+$")


def validate_fields(payload: dict, rules: list[dict]) -> dict:
    errors = []
    for rule in rules:
        field = rule["field"]
        value = payload.get(field)
        if rule.get("required") and value is None:
            errors.append({"field": field, "error": "required"})
            continue
        if value is None:
            continue
        if rule.get("type") == "string" and not isinstance(value, str):
            errors.append({"field": field, "error": "must_be_string"})
        elif rule.get("type") == "email" and (not isinstance(value, str) or not EMAIL_RE.match(value)):
            errors.append({"field": field, "error": "invalid_email"})
        elif rule.get("type") == "url" and (not isinstance(value, str) or not URL_RE.match(value)):
            errors.append({"field": field, "error": "invalid_url"})
        elif rule.get("type") == "number" and not isinstance(value, (int, float)):
            errors.append({"field": field, "error": "must_be_number"})
        if "min_length" in rule and isinstance(value, str) and len(value) < rule["min_length"]:
            errors.append({"field": field, "error": f"min_length_{rule['min_length']}"})
        if "max_length" in rule and isinstance(value, str) and len(value) > rule["max_length"]:
            errors.append({"field": field, "error": f"max_length_{rule['max_length']}"})
    return {"valid": len(errors) == 0, "errors": errors, "error_count": len(errors)}
