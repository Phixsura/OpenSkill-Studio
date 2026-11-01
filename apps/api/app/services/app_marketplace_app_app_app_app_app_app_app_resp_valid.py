"""API response validator — validate API responses against schemas."""
from __future__ import annotations


def validate_response(response: dict, schema: dict) -> dict:
    errors = []
    expected_status = schema.get("status")
    if expected_status and response.get("status") != expected_status:
        errors.append({"field": "status", "expected": expected_status, "actual": response.get("status")})
    body = response.get("body", {})
    for field, rules in schema.get("fields", {}).items():
        value = body.get(field)
        if rules.get("required") and value is None:
            errors.append({"field": field, "error": "required"})
            continue
        if value is not None and "type" in rules:
            expected = rules["type"]
            if expected == "string" and not isinstance(value, str):
                errors.append({"field": field, "error": f"expected {expected}"})
            elif expected == "number" and not isinstance(value, (int, float)):
                errors.append({"field": field, "error": f"expected {expected}"})
            elif expected == "array" and not isinstance(value, list):
                errors.append({"field": field, "error": f"expected {expected}"})
    return {"valid": len(errors) == 0, "errors": errors, "fields_checked": len(schema.get("fields", {}))}


def batch_validate(responses: list[dict], schema: dict) -> dict:
    results = [validate_response(r, schema) for r in responses]
    valid = sum(1 for r in results if r["valid"])
    return {"total": len(results), "valid": valid, "invalid": len(results) - valid,
            "validity_pct": round(valid / max(len(results), 1) * 100, 1)}
