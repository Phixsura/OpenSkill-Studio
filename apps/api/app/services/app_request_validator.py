"""App request validator — validate incoming app API requests.

Provides common validation for requests from third-party apps:
- Request body size limits
- Content-Type validation
- Required headers
- JSON structure validation
"""

import json

MAX_BODY_SIZE = 1_048_576  # 1MB
ALLOWED_CONTENT_TYPES = frozenset({"application/json", "application/x-www-form-urlencoded"})


def validate_request(
    *,
    content_type: str | None = None,
    body_size: int = 0,
    body: bytes | None = None,
    required_headers: dict[str, str] | None = None,
    actual_headers: dict[str, str] | None = None,
) -> dict:
    """Validate an incoming API request.
    
    Returns {"valid": bool, "errors": [...]}
    """
    errors = []

    # Body size
    if body_size > MAX_BODY_SIZE:
        errors.append(f"Request body too large ({body_size} bytes, max {MAX_BODY_SIZE})")

    # Content-Type
    if content_type:
        ct = content_type.split(";")[0].strip().lower()
        if ct not in ALLOWED_CONTENT_TYPES:
            errors.append(f"Unsupported Content-Type: {content_type}")

    # Required headers
    if required_headers is not None and actual_headers is not None:
        for key, expected in required_headers.items():
            actual = actual_headers.get(key)
            if actual is None:
                errors.append(f"Missing required header: {key}")
            elif expected and actual != expected:
                errors.append(f"Invalid header {key}: expected {expected}")

    # JSON parsing
    if body and content_type and "json" in content_type:
        try:
            json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            errors.append("Invalid JSON body")

    return {"valid": len(errors) == 0, "errors": errors}
