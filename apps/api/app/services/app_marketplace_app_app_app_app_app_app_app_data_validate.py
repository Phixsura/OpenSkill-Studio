"""Data validation pipeline — chain validators on data records."""
from __future__ import annotations


def validate_record(record: dict, validators: list[dict]) -> dict:
    errors = []
    warnings = []
    for v in validators:
        field = v["field"]
        value = record.get(field)
        rule = v.get("rule", "required")
        if rule == "required" and value is None:
            errors.append({"field": field, "rule": rule, "message": f"{field} is required"})
        elif rule == "min" and isinstance(value, (int, float)) and value < v.get("value", 0):
            errors.append({"field": field, "rule": rule, "message": f"{field} below minimum {v['value']}"})
        elif rule == "max" and isinstance(value, (int, float)) and value > v.get("value", 0):
            errors.append({"field": field, "rule": rule, "message": f"{field} above maximum {v['value']}"})
        elif rule == "pattern" and isinstance(value, str):
            import re
            if not re.match(v.get("value", ""), value):
                errors.append({"field": field, "rule": rule, "message": f"{field} doesn't match pattern"})
        elif rule == "deprecated":
            if value is not None:
                warnings.append({"field": field, "message": f"{field} is deprecated"})
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings,
            "error_count": len(errors), "warning_count": len(warnings)}


def validate_batch(records: list[dict], validators: list[dict]) -> dict:
    results = [validate_record(r, validators) for r in records]
    valid = sum(1 for r in results if r["valid"])
    return {"total": len(records), "valid": valid, "invalid": len(records) - valid,
            "pass_rate": round(valid / max(len(records), 1) * 100)}
