"""App rate limit config — per-endpoint rate limit configuration."""

import html

DEFAULT_LIMITS = {
    "GET": {"rpm": 600, "burst": 50},
    "POST": {"rpm": 120, "burst": 20},
    "PUT": {"rpm": 120, "burst": 20},
    "DELETE": {"rpm": 30, "burst": 5},
}


def build_rate_limit_config(*, endpoints: list[dict]) -> dict:
    items = []
    for ep in endpoints:
        method = ep.get("method", "GET")
        defaults = DEFAULT_LIMITS.get(method, DEFAULT_LIMITS["GET"])
        rpm = ep.get("rpm", defaults["rpm"])
        burst = ep.get("burst", defaults["burst"])
        items.append({
            "method": method, "path": html.escape(ep.get("path", "")),
            "rpm": rpm, "burst": burst,
            "custom": ep.get("rpm") is not None or ep.get("burst") is not None,
        })
    total_custom = sum(1 for i in items if i["custom"])
    return {"endpoints": items, "total": len(items), "custom_count": total_custom,
            "default_limits": DEFAULT_LIMITS}


def validate_rate_limit(*, rpm: int, burst: int) -> dict:
    errors = []
    if rpm < 1 or rpm > 10000:
        errors.append("RPM must be 1-10,000")
    if burst < 1 or burst > 1000:
        errors.append("Burst must be 1-1,000")
    if burst > rpm:
        errors.append("Burst cannot exceed RPM")
    return {"valid": len(errors) == 0, "errors": errors, "rpm": rpm, "burst": burst}
