"""API endpoint cache policy — define caching policies per endpoint."""
from __future__ import annotations


class CachePolicyManager:
    def __init__(self):
        self._policies: dict[str, dict] = {}

    def set_policy(self, endpoint: str, ttl_seconds: int, cacheable: bool = True,
                   vary_by: list[str] | None = None) -> dict:
        self._policies[endpoint] = {"endpoint": endpoint, "ttl": ttl_seconds,
                                     "cacheable": cacheable, "vary_by": vary_by or []}
        return self._policies[endpoint]

    def get_policy(self, endpoint: str) -> dict:
        return self._policies.get(endpoint, {"endpoint": endpoint, "ttl": 0,
                                              "cacheable": False, "vary_by": []})

    def cache_headers(self, endpoint: str) -> dict:
        policy = self.get_policy(endpoint)
        if not policy["cacheable"]:
            return {"Cache-Control": "no-store", "cacheable": False}
        headers = {"Cache-Control": f"public, max-age={policy['ttl']}"}
        if policy["vary_by"]:
            headers["Vary"] = ", ".join(policy["vary_by"])
        return {**headers, "cacheable": True}

    def stats(self) -> dict:
        cacheable = sum(1 for p in self._policies.values() if p["cacheable"])
        return {"total": len(self._policies), "cacheable": cacheable}
