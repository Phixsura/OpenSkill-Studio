"""Service catalog registry — register, discover, and document microservices."""
from __future__ import annotations


class ServiceCatalog:
    def __init__(self):
        self._services: dict[str, dict] = {}

    def register(self, service_id: str, *, name: str, team: str,
                  description: str = "", tier: str = "tier2",
                  dependencies: list[str] | None = None,
                  docs_url: str = "", health_url: str = "") -> dict:
        self._services[service_id] = {
            "id": service_id, "name": name, "team": team,
            "description": description, "tier": tier,
            "dependencies": dependencies or [],
            "docs_url": docs_url, "health_url": health_url,
        }
        return {"registered": service_id, "name": name}

    def search(self, *, team: str | None = None, tier: str | None = None,
                query: str | None = None) -> list[dict]:
        results = list(self._services.values())
        if team:
            results = [s for s in results if s["team"] == team]
        if tier:
            results = [s for s in results if s["tier"] == tier]
        if query:
            q = query.lower()
            results = [s for s in results if q in s["name"].lower() or q in s["description"].lower()]
        return results

    def dependency_map(self, service_id: str) -> dict:
        svc = self._services.get(service_id)
        if not svc:
            return {"error": "Service not found"}
        deps = svc["dependencies"]
        resolved = [self._services.get(d, {"id": d, "name": d}) for d in deps]
        return {"service": service_id, "dependencies": resolved,
                "count": len(deps)}

    def stats(self) -> dict:
        by_team: dict[str, int] = {}
        by_tier: dict[str, int] = {}
        for s in self._services.values():
            by_team[s["team"]] = by_team.get(s["team"], 0) + 1
            by_tier[s["tier"]] = by_tier.get(s["tier"], 0) + 1
        return {"total": len(self._services), "by_team": by_team, "by_tier": by_tier}
