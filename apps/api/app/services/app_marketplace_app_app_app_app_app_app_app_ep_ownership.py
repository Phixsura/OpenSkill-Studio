"""Endpoint ownership registry — map API endpoints to owning teams."""
from __future__ import annotations
from collections import defaultdict


class EndpointOwnershipRegistry:
    def __init__(self):
        self._ownership: dict[str, dict] = {}

    def register(self, endpoint: str, team: str, oncall: str = "", tier: str = "standard") -> dict:
        self._ownership[endpoint] = {"endpoint": endpoint, "team": team,
                                      "oncall": oncall, "tier": tier}
        return self._ownership[endpoint]

    def get_owner(self, endpoint: str) -> dict:
        return self._ownership.get(endpoint, {"endpoint": endpoint, "team": "unowned"})

    def by_team(self, team: str) -> list[dict]:
        return [o for o in self._ownership.values() if o["team"] == team]

    def unowned(self, all_endpoints: list[str]) -> list[str]:
        owned = set(self._ownership.keys())
        return sorted(set(all_endpoints) - owned)

    def stats(self) -> dict:
        teams: dict[str, int] = defaultdict(int)
        for o in self._ownership.values():
            teams[o["team"]] += 1
        return {"total": len(self._ownership), "teams": len(teams), "by_team": dict(teams)}
