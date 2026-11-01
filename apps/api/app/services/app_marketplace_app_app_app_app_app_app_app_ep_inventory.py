"""API endpoint inventory — maintain inventory of all platform API endpoints."""
from __future__ import annotations
from collections import defaultdict


class EndpointInventory:
    def __init__(self):
        self._endpoints: list[dict] = []

    def add(self, method: str, path: str, service: str, version: str = "v1",
            deprecated: bool = False, auth: str = "required") -> dict:
        ep = {"method": method, "path": path, "service": service,
              "version": version, "deprecated": deprecated, "auth": auth}
        self._endpoints.append(ep)
        return ep

    def search(self, path_contains: str = "", service: str = "",
               include_deprecated: bool = False) -> list[dict]:
        results = self._endpoints
        if not include_deprecated:
            results = [e for e in results if not e["deprecated"]]
        if path_contains:
            results = [e for e in results if path_contains in e["path"]]
        if service:
            results = [e for e in results if e["service"] == service]
        return sorted(results, key=lambda e: e["path"])

    def stats(self) -> dict:
        by_service: dict[str, int] = defaultdict(int)
        deprecated = 0
        for e in self._endpoints:
            by_service[e["service"]] += 1
            if e["deprecated"]:
                deprecated += 1
        return {"total": len(self._endpoints), "deprecated": deprecated,
                "services": len(by_service), "by_service": dict(by_service)}
