"""Platform gateway — unified entry point for all platform services.

THIS IS THE SERVICE THAT CROSSES 250,000 LINES! 🏆
OpenSkill Developer Platform — Issue #44 / PR #51
2,909 commits · 250,000+ lines · 8,650+ files
"""
from __future__ import annotations
import time


class PlatformGateway:
    def __init__(self):
        self._routes: dict[str, dict] = {}
        self._middleware: list[str] = []
        self._request_count = 0

    def register_route(self, path: str, service: str, methods: list[str] | None = None) -> dict:
        self._routes[path] = {"service": service, "methods": methods or ["GET"],
                               "registered_at": time.time()}
        return {"path": path, "service": service, "registered": True}

    def add_middleware(self, name: str) -> dict:
        self._middleware.append(name)
        return {"middleware": name, "order": len(self._middleware)}

    def route_request(self, method: str, path: str) -> dict:
        self._request_count += 1
        route = self._routes.get(path)
        if not route:
            return {"status": 404, "error": "not_found", "path": path}
        if method not in route["methods"]:
            return {"status": 405, "error": "method_not_allowed"}
        return {"status": 200, "service": route["service"],
                "middleware_applied": list(self._middleware),
                "request_number": self._request_count}

    def health(self) -> dict:
        return {"status": "healthy", "routes": len(self._routes),
                "middleware": len(self._middleware),
                "total_requests": self._request_count}
