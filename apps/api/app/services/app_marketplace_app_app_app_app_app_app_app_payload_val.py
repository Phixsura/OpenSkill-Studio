"""Request payload validator — validate JSON payloads against schemas."""
from __future__ import annotations


def validate_payload(payload: dict, schema: dict) -> dict:
    errors = []
    for field, rules in schema.items():
        value = payload.get(field)
        required = rules.get("required", False)
        if value is None and required:
            errors.append({"field": field, "error": "required"})
            continue
        if value is None:
            continue
        ftype = rules.get("type")
        if ftype == "string" and not isinstance(value, str):
            errors.append({"field": field, "error": "expected_string"})
        elif ftype == "int" and not isinstance(value, int):
            errors.append({"field": field, "error": "expected_int"})
        elif ftype == "list" and not isinstance(value, list):
            errors.append({"field": field, "error": "expected_list"})
        if "max_length" in rules and isinstance(value, str) and len(value) > rules["max_length"]:
            errors.append({"field": field, "error": f"max_length_{rules['max_length']}"})
        if "min_value" in rules and isinstance(value, (int, float)) and value < rules["min_value"]:
            errors.append({"field": field, "error": f"min_value_{rules['min_value']}"})
    return {"valid": len(errors) == 0, "errors": errors, "error_count": len(errors),
            "fields_checked": len(schema)}
