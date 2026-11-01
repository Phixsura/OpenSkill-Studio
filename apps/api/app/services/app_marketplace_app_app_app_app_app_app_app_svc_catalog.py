"""Service catalog registry — register and discover platform services."""
from __future__ import annotations


class ServiceCatalog:
    def __init__(self):
        self._services: dict[str, dict] = {}

    def register(self, name: str, owner: str, tier: str = "standard",
                 tags: list[str] | None = None) -> dict:
        self._services[name] = {"name": name, "owner": owner, "tier": tier,
                                 "tags": tags or [], "status": "active",
                                 "dependencies": []}
        return self._services[name]

    def add_dependency(self, name: str, depends_on: str) -> dict:
        svc = self._services[name]
        if depends_on not in svc["dependencies"]:
            svc["dependencies"].append(depends_on)
        return {"service": name, "dependencies": svc["dependencies"]}

    def search(self, query: str = "", tag: str = "") -> list[dict]:
        results = []
        for svc in self._services.values():
            if query and query.lower() not in svc["name"].lower():
                continue
            if tag and tag not in svc["tags"]:
                continue
            results.append(svc)
        return sorted(results, key=lambda s: s["name"])

    def stats(self) -> dict:
        by_tier: dict[str, int] = {}
        for s in self._services.values():
            by_tier[s["tier"]] = by_tier.get(s["tier"], 0) + 1
        return {"total": len(self._services), "by_tier": by_tier}
