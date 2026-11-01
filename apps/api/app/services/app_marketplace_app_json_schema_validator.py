"""JSON schema validator — validate API payloads against schemas."""


def validate_payload(*, payload: dict, schema: dict) -> dict:
    errors = []
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for field in required:
        if field not in payload:
            errors.append({"field": field, "error": "Required field missing"})

    for field, value in payload.items():
        if field not in properties:
            if not schema.get("additionalProperties", True):
                errors.append({"field": field, "error": "Unknown field (additionalProperties: false)"})
            continue
        expected_type = properties[field].get("type")
        type_map = {"string": str, "integer": int, "number": (int, float),
                     "boolean": bool, "array": list, "object": dict}
        expected = type_map.get(expected_type)
        if expected and not isinstance(value, expected):
            errors.append({"field": field, "error": f"Expected {expected_type}, got {type(value).__name__}"})
        min_len = properties[field].get("minLength")
        if min_len and isinstance(value, str) and len(value) < min_len:
            errors.append({"field": field, "error": f"Minimum length {min_len}"})
        max_len = properties[field].get("maxLength")
        if max_len and isinstance(value, str) and len(value) > max_len:
            errors.append({"field": field, "error": f"Maximum length {max_len}"})

    return {"valid": len(errors) == 0, "errors": errors, "error_count": len(errors)}
