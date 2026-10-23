"""CORS config — manage Cross-Origin Resource Sharing policies."""

import re

ORIGIN_RE = re.compile(r"^https?://[a-zA-Z0-9.-]+(:\d+)?$")


def validate_cors_config(*, allowed_origins: list[str], allowed_methods: list[str],
                           max_age_sec: int = 3600) -> dict:
    valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}
    errors = []
    valid_origins = []
    for origin in allowed_origins:
        if origin == "*":
            valid_origins.append("*")
        elif ORIGIN_RE.match(origin):
            valid_origins.append(origin)
        else:
            errors.append(f"Invalid origin: {origin}")
    invalid_methods = set(m.upper() for m in allowed_methods) - valid_methods
    if invalid_methods:
        errors.append(f"Invalid methods: {', '.join(sorted(invalid_methods))}")
    if max_age_sec > 86400:
        errors.append("max_age cannot exceed 86400 seconds (24h)")
    wildcard_warning = "*" in valid_origins and len(valid_origins) > 1
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "origins": valid_origins,
        "methods": sorted(set(m.upper() for m in allowed_methods) & valid_methods),
        "max_age_sec": max_age_sec,
        "wildcard_warning": wildcard_warning,
    }
