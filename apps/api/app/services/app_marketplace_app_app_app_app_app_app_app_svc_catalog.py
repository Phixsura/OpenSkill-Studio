"""Service catalog — registry of all platform services."""
from __future__ import annotations


def build_catalog(services: list[dict]) -> dict:
    by_tier: dict[str, list[str]] = {}
    by_owner: dict[str, int] = {}
    for s in services:
        tier = s.get("tier", "standard")
        by_tier.setdefault(tier, []).append(s["name"])
        owner = s.get("owner", "unassigned")
        by_owner[owner] = by_owner.get(owner, 0) + 1
    healthy = sum(1 for s in services if s.get("status") == "healthy")
    return {"services": services, "total": len(services), "healthy": healthy,
            "unhealthy": len(services) - healthy,
            "by_tier": {k: len(v) for k, v in by_tier.items()},
            "by_owner": by_owner}


def search_catalog(services: list[dict], query: str) -> list[dict]:
    q = query.lower()
    return [s for s in services if q in s.get("name", "").lower()
            or q in s.get("description", "").lower()
            or q in s.get("owner", "").lower()]
