"""API response validator — validate API responses match expected format."""
from __future__ import annotations


def validate_api_response(response: dict) -> dict:
    errors = []
    # Check standard envelope
    if "data" not in response and "error" not in response:
        errors.append("Missing 'data' or 'error' field")
    if "error" in response:
        err = response["error"]
        if not isinstance(err, dict):
            errors.append("'error' must be an object")
        elif "code" not in err or "message" not in err:
            errors.append("Error must have 'code' and 'message'")
    if isinstance(response.get("data"), list):
        if "meta" not in response:
            errors.append("List response should have 'meta' field")
        else:
            meta = response["meta"]
            for field in ("total", "page"):
                if field not in meta:
                    errors.append(f"Meta missing '{field}'")
    return {"valid": len(errors) == 0, "errors": errors,
            "response_type": "error" if "error" in response else "list" if isinstance(response.get("data"), list) else "single"}


def check_status_code(status: int, body: dict) -> dict:
    issues = []
    if status >= 400 and "error" not in body:
        issues.append(f"Status {status} should have error body")
    if status < 400 and "error" in body:
        issues.append(f"Status {status} should not have error body")
    if status == 201 and isinstance(body.get("data"), list):
        issues.append("201 Created should return single resource, not list")
    return {"valid": len(issues) == 0, "issues": issues, "status": status}
