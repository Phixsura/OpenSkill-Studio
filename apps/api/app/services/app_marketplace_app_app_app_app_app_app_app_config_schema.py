"""Config schema validator — validate app config against a schema."""
from __future__ import annotations

TYPES = {"string", "number", "boolean", "array", "object"}


def validate_config(schema: list[dict], config: dict) -> dict:
    errors = []
    warnings = []
    for field in schema:
        key = field["key"]
        required = field.get("required", False)
        ftype = field.get("type", "string")
        if key not in config:
            if required:
                errors.append({"key": key, "error": "missing_required"})
            continue
        val = config[key]
        type_ok = _check_type(val, ftype)
        if not type_ok:
            errors.append({"key": key, "error": f"expected_{ftype}", "got": type(val).__name__})
        if "min" in field and isinstance(val, (int, float)) and val < field["min"]:
            errors.append({"key": key, "error": "below_min", "min": field["min"]})
        if "max" in field and isinstance(val, (int, float)) and val > field["max"]:
            errors.append({"key": key, "error": "above_max", "max": field["max"]})
        if "enum" in field and val not in field["enum"]:
            errors.append({"key": key, "error": "invalid_enum", "allowed": field["enum"]})
        if field.get("deprecated"):
            warnings.append({"key": key, "warning": "deprecated"})
    extra = set(config) - {f["key"] for f in schema}
    for k in sorted(extra):
        warnings.append({"key": k, "warning": "unknown_field"})
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings,
            "error_count": len(errors), "warning_count": len(warnings)}


def _check_type(val: object, expected: str) -> bool:
    if expected == "string":
        return isinstance(val, str)
    if expected == "number":
        return isinstance(val, (int, float)) and not isinstance(val, bool)
    if expected == "boolean":
        return isinstance(val, bool)
    if expected == "array":
        return isinstance(val, list)
    if expected == "object":
        return isinstance(val, dict)
    return True
