"""API gateway config — manage routes, auth, and transformations."""
from __future__ import annotations


def create_route(path: str, upstream: str, methods: list[str] | None = None,
                 auth_required: bool = True, rate_limit: int = 0) -> dict:
    return {"path": path, "upstream": upstream,
            "methods": [m.upper() for m in (methods or ["GET"])],
            "auth_required": auth_required, "rate_limit": rate_limit}


def build_gateway(routes: list[dict]) -> dict:
    by_auth = {"public": 0, "authenticated": 0}
    by_method: dict[str, int] = {}
    for r in routes:
        if r["auth_required"]:
            by_auth["authenticated"] += 1
        else:
            by_auth["public"] += 1
        for m in r["methods"]:
            by_method[m] = by_method.get(m, 0) + 1
    return {"routes": routes, "total": len(routes), "by_auth": by_auth,
            "by_method": by_method, "rate_limited": sum(1 for r in routes if r["rate_limit"] > 0)}


def match_route(gateway: dict, method: str, path: str) -> dict:
    for r in gateway["routes"]:
        if r["path"] == path and method.upper() in r["methods"]:
            return {"matched": True, "route": r}
    return {"matched": False, "error": "no_matching_route"}
