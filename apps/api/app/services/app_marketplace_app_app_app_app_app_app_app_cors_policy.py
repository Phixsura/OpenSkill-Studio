"""CORS policy manager — configure cross-origin resource sharing."""
from __future__ import annotations
from urllib.parse import urlparse


def create_policy(allowed_origins: list[str], allowed_methods: list[str] | None = None,
                  allow_credentials: bool = False, max_age: int = 86400) -> dict:
    valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}
    methods = [m.upper() for m in (allowed_methods or ["GET", "POST"])]
    invalid = [m for m in methods if m not in valid_methods]
    if invalid:
        return {"created": False, "error": f"invalid methods: {invalid}"}
    origins = []
    for o in allowed_origins:
        if o == "*":
            origins.append("*")
        else:
            parsed = urlparse(o)
            if parsed.scheme not in ("http", "https"):
                return {"created": False, "error": f"invalid origin scheme: {o}"}
            origins.append(o)
    if allow_credentials and "*" in origins:
        return {"created": False, "error": "cannot use wildcard with credentials"}
    return {"created": True, "origins": origins, "methods": methods,
            "credentials": allow_credentials, "max_age": max_age}


def check_origin(policy: dict, origin: str) -> dict:
    if "*" in policy["origins"]:
        return {"allowed": True, "matched": "*"}
    if origin in policy["origins"]:
        return {"allowed": True, "matched": origin}
    return {"allowed": False, "reason": "origin_not_allowed"}
