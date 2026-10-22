"""API gateway — route and transform requests between apps and the platform."""

import re


def create_route(*, path_pattern: str, target_app_id: str, methods: list[str],
                    auth_required: bool = True, rate_limit: int = 100) -> dict:
    if not path_pattern.startswith("/"):
        return {"error": "Path must start with /"}
    return {"path_pattern": path_pattern, "target_app_id": target_app_id,
            "methods": [m.upper() for m in methods], "auth_required": auth_required,
            "rate_limit": rate_limit, "status": "active", "error": None}


def match_route(*, path: str, method: str, routes: list[dict]) -> dict | None:
    for route in routes:
        pattern = route["path_pattern"].replace("{id}", r"[^/]+")
        if re.match(f"^{pattern}$", path) and method.upper() in route["methods"]:
            return route
    return None


def build_gateway_config(*, routes: list[dict], global_rate_limit: int = 1000,
                            cors_origins: list[str] | None = None) -> dict:
    return {"routes": routes, "route_count": len(routes),
            "global_rate_limit": global_rate_limit,
            "cors": {"origins": cors_origins or ["*"], "methods": ["GET", "POST", "PUT", "DELETE"]},
            "middleware": ["auth", "rate_limit", "cors", "logging"]}
