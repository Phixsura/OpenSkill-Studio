"""Request body validator — validate JSON request bodies against schemas."""
from __future__ import annotations


def validate_body(body: dict, schema: dict) -> dict:
    errors = []
    for field, rules in schema.get("properties", {}).items():
        required = field in schema.get("required", [])
        value = body.get(field)
        if value is None and required:
            errors.append({"field": field, "error": "required"})
            continue
        if value is None:
            continue
        expected = rules.get("type")
        if expected == "string" and not isinstance(value, str):
            errors.append({"field": field, "error": "expected string"})
        elif expected == "number" and not isinstance(value, (int, float)):
            errors.append({"field": field, "error": "expected number"})
        elif expected == "array" and not isinstance(value, list):
            errors.append({"field": field, "error": "expected array"})
        elif expected == "object" and not isinstance(value, dict):
            errors.append({"field": field, "error": "expected object"})
        if "minLength" in rules and isinstance(value, str) and len(value) < rules["minLength"]:
            errors.append({"field": field, "error": f"minLength {rules['minLength']}"})
        if "minimum" in rules and isinstance(value, (int, float)) and value < rules["minimum"]:
            errors.append({"field": field, "error": f"minimum {rules['minimum']}"})
    return {"valid": len(errors) == 0, "errors": errors}
