"""Request validator — validate incoming API requests against schemas."""

import re


def validate_request(*, method: str, path: str, headers: dict,
                       body: dict | None = None, rules: dict | None = None) -> dict:
    errors = []
    # Content-Type check for POST/PUT
    if method.upper() in ("POST", "PUT", "PATCH"):
        ct = headers.get("content-type", headers.get("Content-Type", ""))
        if "application/json" not in ct:
            errors.append({"field": "Content-Type", "error": "Must be application/json"})
    # Auth check
    auth = headers.get("authorization", headers.get("Authorization", ""))
    if rules and rules.get("auth_required") and not auth:
        errors.append({"field": "Authorization", "error": "Required"})
    # Body validation
    if rules and body:
        for field, constraints in rules.get("body_rules", {}).items():
            value = body.get(field)
            if constraints.get("required") and not value:
                errors.append({"field": field, "error": "Required field missing"})
            if constraints.get("min_length") and isinstance(value, str) and len(value) < constraints["min_length"]:
                errors.append({"field": field, "error": f"Min length {constraints['min_length']}"})
    return {"valid": len(errors) == 0, "errors": errors, "error_count": len(errors)}
