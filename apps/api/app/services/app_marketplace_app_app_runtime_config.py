"""Runtime config — dynamic configuration with type validation."""

import html
from typing import Any

TYPE_VALIDATORS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "float": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "list": lambda v: isinstance(v, list),
}


def validate_config(*, schema: dict[str, dict], values: dict[str, Any]) -> dict:
    errors = []
    validated = {}
    for key, spec in schema.items():
        value = values.get(key, spec.get("default"))
        expected_type = spec.get("type", "string")
        required = spec.get("required", False)
        if value is None and required:
            errors.append({"key": key, "error": "Required field missing"})
            continue
        if value is not None:
            validator = TYPE_VALIDATORS.get(expected_type)
            if validator and not validator(value):
                errors.append({"key": key, "error": f"Expected {expected_type}, got {type(value).__name__}"})
                continue
        validated[key] = value
    return {"valid": len(errors) == 0, "errors": errors, "config": validated,
            "key_count": len(validated)}


def merge_configs(*, base: dict, override: dict) -> dict:
    merged = dict(base)
    merged.update({k: v for k, v in override.items() if v is not None})
    return {"config": merged, "overridden_keys": [k for k in override if k in base and override[k] is not None]}
