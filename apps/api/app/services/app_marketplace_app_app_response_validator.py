"""Response validator — validate API responses against expected schema."""

import html


def validate_response(*, response: dict, schema: dict) -> dict:
    errors = []
    for field, spec in schema.items():
        expected_type = spec.get("type")
        required = spec.get("required", False)
        value = response.get(field)
        if value is None and required:
            errors.append({"field": field, "error": "Missing required field"})
            continue
        if value is not None and expected_type:
            type_map = {"string": str, "integer": int, "float": (int, float),
                        "boolean": bool, "list": list, "dict": dict}
            expected = type_map.get(expected_type)
            if expected and not isinstance(value, expected):
                errors.append({"field": field,
                               "error": f"Expected {expected_type}, got {type(value).__name__}"})
    return {"valid": len(errors) == 0, "errors": errors,
            "checked_fields": len(schema), "passed_fields": len(schema) - len(errors)}


def build_validation_report(*, responses: list[dict], schema: dict) -> dict:
    results = [validate_response(response=r, schema=schema) for r in responses]
    valid_count = sum(1 for r in results if r["valid"])
    return {"total_responses": len(responses), "valid": valid_count,
            "invalid": len(responses) - valid_count,
            "pass_rate": round(valid_count / max(len(responses), 1) * 100, 1)}
