"""Request validator — validate API request payloads against schemas."""
from __future__ import annotations


def validate_request(payload: dict, schema: dict) -> dict:
    errors = []
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    for field in required:
        if field not in payload:
            errors.append({"field": field, "error": "required", "message": f"{field} is required"})
    for field, value in payload.items():
        if field not in properties:
            continue
        rules = properties[field]
        ftype = rules.get("type")
        if ftype == "string" and not isinstance(value, str):
            errors.append({"field": field, "error": "type", "message": f"{field} must be a string"})
        elif ftype == "integer" and not isinstance(value, int):
            errors.append({"field": field, "error": "type", "message": f"{field} must be an integer"})
        elif ftype == "string" and isinstance(value, str):
            min_len = rules.get("min_length", 0)
            max_len = rules.get("max_length", float("inf"))
            if len(value) < min_len:
                errors.append({"field": field, "error": "min_length", "message": f"{field} must be at least {min_len} chars"})
            if len(value) > max_len:
                errors.append({"field": field, "error": "max_length", "message": f"{field} must be at most {max_len} chars"})
        if "enum" in rules and value not in rules["enum"]:
            errors.append({"field": field, "error": "enum", "message": f"{field} must be one of {rules['enum']}"})
    return {"valid": len(errors) == 0, "errors": errors, "error_count": len(errors)}
