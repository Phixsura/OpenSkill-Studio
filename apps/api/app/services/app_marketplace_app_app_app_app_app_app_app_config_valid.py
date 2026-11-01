"""Platform config validator — validate configuration against schemas."""
from __future__ import annotations


def validate_config(config: dict, schema: dict) -> dict:
    errors = []
    for field, rules in schema.items():
        value = config.get(field)
        required = rules.get("required", False)
        if required and value is None:
            errors.append({"field": field, "error": "required", "severity": "error"})
            continue
        if value is None:
            continue
        expected_type = rules.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append({"field": field, "error": f"expected string, got {type(value).__name__}", "severity": "error"})
        elif expected_type == "int" and not isinstance(value, int):
            errors.append({"field": field, "error": f"expected int, got {type(value).__name__}", "severity": "error"})
        elif expected_type == "bool" and not isinstance(value, bool):
            errors.append({"field": field, "error": f"expected bool, got {type(value).__name__}", "severity": "error"})
        if "min" in rules and isinstance(value, (int, float)) and value < rules["min"]:
            errors.append({"field": field, "error": f"below minimum {rules['min']}", "severity": "warning"})
        if "max" in rules and isinstance(value, (int, float)) and value > rules["max"]:
            errors.append({"field": field, "error": f"above maximum {rules['max']}", "severity": "warning"})
        if "enum" in rules and value not in rules["enum"]:
            errors.append({"field": field, "error": f"must be one of {rules['enum']}", "severity": "error"})
    return {"valid": len([e for e in errors if e["severity"] == "error"]) == 0,
            "errors": errors, "fields_checked": len(schema)}
