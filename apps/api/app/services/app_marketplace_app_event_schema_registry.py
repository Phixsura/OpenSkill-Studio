"""Event schema registry — define and validate event payload schemas."""

import json


def register_event_schema(*, event_type: str, schema: dict, version: int = 1) -> dict:
    if not event_type or "." not in event_type:
        return {"error": "Event type must be namespaced (e.g., 'app.installed')"}
    if "properties" not in schema:
        return {"error": "Schema must include 'properties'"}
    return {"event_type": event_type, "version": version, "schema": schema, "error": None}


def validate_event_payload(*, payload: dict, schema: dict) -> dict:
    errors = []
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    for key in required:
        if key not in payload:
            errors.append(f"Missing required field: {key}")
    for key, value in payload.items():
        if key in properties:
            prop = properties[key]
            expected = prop.get("type")
            if expected == "string" and not isinstance(value, str):
                errors.append(f"'{key}' must be string")
            elif expected == "number" and not isinstance(value, (int, float)):
                errors.append(f"'{key}' must be number")
    return {"valid": len(errors) == 0, "errors": errors}


def list_event_types(*, schemas: list[dict]) -> list[dict]:
    return [{"event_type": s["event_type"], "version": s.get("version", 1),
             "field_count": len(s.get("schema", {}).get("properties", {}))} for s in schemas]
