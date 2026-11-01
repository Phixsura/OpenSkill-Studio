"""Request validation — schema-based request validation middleware for app APIs."""

import re


def validate_request(*, body: dict, schema: dict) -> dict:
    errors = []
    for field, rules in schema.get("fields", {}).items():
        value = body.get(field)
        required = rules.get("required", False)
        if required and value is None:
            errors.append({"field": field, "error": "required"})
            continue
        if value is None:
            continue
        expected_type = rules.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append({"field": field, "error": f"expected string, got {type(value).__name__}"})
        elif expected_type == "integer" and not isinstance(value, int):
            errors.append({"field": field, "error": f"expected integer, got {type(value).__name__}"})
        elif expected_type == "email" and isinstance(value, str):
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', value):
                errors.append({"field": field, "error": "invalid email format"})
        min_len = rules.get("min_length")
        if min_len and isinstance(value, str) and len(value) < min_len:
            errors.append({"field": field, "error": f"minimum length {min_len}"})
        max_len = rules.get("max_length")
        if max_len and isinstance(value, str) and len(value) > max_len:
            errors.append({"field": field, "error": f"maximum length {max_len}"})
    return {"valid": len(errors) == 0, "errors": errors}


def build_validation_schema(*, fields: list[dict]) -> dict:
    schema_fields = {}
    for f in fields:
        schema_fields[f["name"]] = {k: v for k, v in f.items() if k != "name"}
    return {"fields": schema_fields, "field_count": len(schema_fields)}
