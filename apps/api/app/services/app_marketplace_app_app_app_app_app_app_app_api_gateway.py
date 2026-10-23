"""API gateway config — manage routes, middleware, and upstream services."""
from __future__ import annotations


class ApiGateway:
    def __init__(self):
        self._routes: list[dict] = []
        self._middleware: list[str] = []

    def add_route(self, *, path: str, upstream: str, methods: list[str] | None = None,
                   rate_limit: int = 0, auth_required: bool = True,
                   strip_prefix: bool = False) -> dict:
        route = {"path": path, "upstream": upstream,
                 "methods": methods or ["GET", "POST", "PUT", "DELETE"],
                 "rate_limit": rate_limit, "auth_required": auth_required,
                 "strip_prefix": strip_prefix, "enabled": True}
        self._routes.append(route)
        return {"added": path, "upstream": upstream}

    def add_middleware(self, name: str) -> dict:
        if name not in self._middleware:
            self._middleware.append(name)
        return {"middleware": name, "order": len(self._middleware)}

    def resolve(self, path: str, method: str = "GET") -> dict:
        for r in self._routes:
            if path.startswith(r["path"]) and r["enabled"]:
                if method.upper() not in r["methods"]:
                    return {"matched": True, "allowed": False, "reason": "method_not_allowed"}
                return {"matched": True, "allowed": True, "upstream": r["upstream"],
                        "auth_required": r["auth_required"], "rate_limit": r["rate_limit"]}
        return {"matched": False, "reason": "no_route"}

    def config(self) -> dict:
        return {"routes": self._routes, "middleware": self._middleware,
                "total_routes": len(self._routes)}
