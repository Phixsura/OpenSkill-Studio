"""Runtime config validator — validate config at startup and runtime."""
from __future__ import annotations
import re


def validate_runtime_config(config: dict, schema: dict[str, dict]) -> dict:
    errors = []
    warnings = []
    for key, rules in schema.items():
        value = config.get(key)
        required = rules.get("required", False)
        if value is None:
            if required:
                errors.append({"key": key, "error": "missing_required"})
            continue
        expected_type = rules.get("type")
        if expected_type == "int" and not isinstance(value, int):
            errors.append({"key": key, "error": "expected_int"})
        elif expected_type == "str" and not isinstance(value, str):
            errors.append({"key": key, "error": "expected_str"})
        elif expected_type == "bool" and not isinstance(value, bool):
            errors.append({"key": key, "error": "expected_bool"})
        if "pattern" in rules and isinstance(value, str):
            if not re.match(rules["pattern"], value):
                errors.append({"key": key, "error": "pattern_mismatch"})
        if rules.get("deprecated"):
            warnings.append({"key": key, "warning": "deprecated_config"})
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings,
            "checked": len(schema)}
