"""CORS config — manage allowed origins for app API endpoints."""

import re

ORIGIN_RE = re.compile(r'^https?://[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?(:\d+)?$')


def validate_origin(origin: str) -> dict:
    if origin == "*":
        return {"valid": True, "warning": "Wildcard origin allows all domains — not recommended for production"}
    if not ORIGIN_RE.match(origin):
        return {"valid": False, "warning": f"Invalid origin format: {origin}"}
    return {"valid": True, "warning": None}


def build_cors_config(*, allowed_origins: list[str], allowed_methods: list[str] | None = None,
                        max_age: int = 3600) -> dict:
    methods = allowed_methods or ["GET", "POST", "PUT", "DELETE"]
    validations = [validate_origin(o) for o in allowed_origins]
    invalid = [allowed_origins[i] for i, v in enumerate(validations) if not v["valid"]]
    warnings = [v["warning"] for v in validations if v.get("warning")]
    return {
        "allowed_origins": allowed_origins, "allowed_methods": methods,
        "max_age": max_age, "allow_credentials": "*" not in allowed_origins,
        "invalid_origins": invalid, "warnings": warnings, "valid": len(invalid) == 0,
    }
