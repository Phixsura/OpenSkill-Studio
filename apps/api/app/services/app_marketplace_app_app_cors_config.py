"""CORS config — Cross-Origin Resource Sharing policy builder."""

from urllib.parse import urlparse


SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
ALL_METHODS = {"GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"}


def build_cors_policy(*, allowed_origins: list[str], allowed_methods: list[str] | None = None,
                        allowed_headers: list[str] | None = None,
                        max_age_s: int = 86400, credentials: bool = False) -> dict:
    methods = set(allowed_methods or ALL_METHODS)
    headers = allowed_headers or ["Content-Type", "Authorization"]
    errors = []
    safe_origins = []
    for origin in allowed_origins:
        if origin == "*":
            safe_origins.append("*")
            if credentials:
                errors.append("Cannot use wildcard origin with credentials")
        else:
            parsed = urlparse(origin)
            if parsed.scheme not in ("https", "http"):
                errors.append(f"Invalid origin scheme: {origin}")
            else:
                safe_origins.append(origin)
    header_value = ", ".join(safe_origins) if safe_origins != ["*"] else "*"
    return {
        "allowed_origins": safe_origins,
        "allowed_methods": sorted(methods),
        "allowed_headers": headers,
        "max_age_s": max_age_s,
        "credentials": credentials,
        "errors": errors,
        "valid": len(errors) == 0,
        "headers": {
            "Access-Control-Allow-Origin": header_value,
            "Access-Control-Allow-Methods": ", ".join(sorted(methods)),
            "Access-Control-Allow-Headers": ", ".join(headers),
            "Access-Control-Max-Age": str(max_age_s),
        },
    }
