"""JSON schema validator — validate payloads against JSON Schema-like definitions."""
from __future__ import annotations


def validate_schema(data: dict, schema: dict) -> dict:
    errors = []
    _validate_object(data, schema, "", errors)
    return {"valid": len(errors) == 0, "errors": errors, "error_count": len(errors)}


def _validate_object(data: dict, schema: dict, path: str, errors: list) -> None:
    props = schema.get("properties", {})
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            errors.append({"path": f"{path}.{field}" if path else field,
                           "error": "required", "message": f"{field} is required"})
    for field, value in data.items():
        if field not in props:
            continue
        field_path = f"{path}.{field}" if path else field
        field_schema = props[field]
        expected_type = field_schema.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append({"path": field_path, "error": "type", "message": f"Expected string"})
        elif expected_type == "integer" and not isinstance(value, int):
            errors.append({"path": field_path, "error": "type", "message": f"Expected integer"})
        elif expected_type == "boolean" and not isinstance(value, bool):
            errors.append({"path": field_path, "error": "type", "message": f"Expected boolean"})
        elif expected_type == "array" and not isinstance(value, list):
            errors.append({"path": field_path, "error": "type", "message": f"Expected array"})
        elif expected_type == "object" and isinstance(value, dict):
            _validate_object(value, field_schema, field_path, errors)
        if expected_type == "string" and isinstance(value, str):
            min_len = field_schema.get("minLength", 0)
            max_len = field_schema.get("maxLength", float("inf"))
            if len(value) < min_len:
                errors.append({"path": field_path, "error": "minLength", "message": f"Min {min_len} chars"})
            if len(value) > max_len:
                errors.append({"path": field_path, "error": "maxLength", "message": f"Max {max_len} chars"})
        if "enum" in field_schema and value not in field_schema["enum"]:
            errors.append({"path": field_path, "error": "enum",
                           "message": f"Must be one of {field_schema['enum']}"})
