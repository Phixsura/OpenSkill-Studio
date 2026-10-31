"""API endpoint catalog — centralized endpoint discovery and metadata."""
from __future__ import annotations


class EndpointCatalog:
    def __init__(self):
        self._endpoints: list[dict] = []

    def register(self, method: str, path: str, service: str, version: str = "v1",
                 auth_required: bool = True, rate_limit: int = 100) -> dict:
        ep = {"method": method, "path": path, "service": service,
              "version": version, "auth_required": auth_required,
              "rate_limit": rate_limit}
        self._endpoints.append(ep)
        return ep

    def search(self, service: str = "", version: str = "", method: str = "") -> list[dict]:
        results = self._endpoints
        if service:
            results = [e for e in results if e["service"] == service]
        if version:
            results = [e for e in results if e["version"] == version]
        if method:
            results = [e for e in results if e["method"] == method]
        return sorted(results, key=lambda e: e["path"])

    def stats(self) -> dict:
        services = set(e["service"] for e in self._endpoints)
        by_method = {}
        for e in self._endpoints:
            by_method[e["method"]] = by_method.get(e["method"], 0) + 1
        return {"total": len(self._endpoints), "services": len(services),
                "by_method": by_method}
