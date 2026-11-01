"""Config schema registry — validate and version app configuration schemas."""

import json


def register_schema(*, app_id: str, version: int, schema: dict) -> dict:
    required_keys = {"type", "properties"}
    if not required_keys.issubset(schema.keys()):
        return {"error": f"Schema must include: {', '.join(required_keys)}"}
    return {"app_id": app_id, "version": version, "schema": schema, "registered": True, "error": None}


def validate_config_against_schema(*, config: dict, schema: dict) -> dict:
    errors = []
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    for key in required:
        if key not in config:
            errors.append(f"Missing required field: {key}")
    for key, value in config.items():
        if key in properties:
            expected_type = properties[key].get("type")
            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"Field '{key}' must be a string")
            elif expected_type == "integer" and not isinstance(value, int):
                errors.append(f"Field '{key}' must be an integer")
            elif expected_type == "boolean" and not isinstance(value, bool):
                errors.append(f"Field '{key}' must be a boolean")
    return {"valid": len(errors) == 0, "errors": errors}


def diff_schemas(*, old_schema: dict, new_schema: dict) -> dict:
    old_props = set(old_schema.get("properties", {}).keys())
    new_props = set(new_schema.get("properties", {}).keys())
    return {"added": sorted(new_props - old_props), "removed": sorted(old_props - new_props),
            "kept": sorted(old_props & new_props), "breaking": len(old_props - new_props) > 0}
