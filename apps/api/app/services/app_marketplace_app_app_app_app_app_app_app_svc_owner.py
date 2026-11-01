"""Service ownership registry — track service owners and on-call rotations."""
from __future__ import annotations


class ServiceOwnerRegistry:
    def __init__(self):
        self._services: dict[str, dict] = {}

    def register(self, service: str, team: str, oncall: str, escalation: list[str] | None = None) -> dict:
        self._services[service] = {"service": service, "team": team,
                                    "oncall": oncall, "escalation": escalation or [oncall]}
        return self._services[service]

    def get_oncall(self, service: str) -> dict:
        svc = self._services.get(service)
        if not svc:
            return {"service": service, "found": False}
        return {"service": service, "found": True, "oncall": svc["oncall"],
                "team": svc["team"], "escalation": svc["escalation"]}

    def by_team(self, team: str) -> list[dict]:
        return [s for s in self._services.values() if s["team"] == team]

    def unowned(self) -> list[str]:
        return [s for s, d in self._services.items() if not d.get("team")]

    def stats(self) -> dict:
        teams = set(s["team"] for s in self._services.values())
        return {"services": len(self._services), "teams": len(teams)}
