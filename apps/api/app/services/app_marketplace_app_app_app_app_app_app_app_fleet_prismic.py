"""Fleet Prismic — track content management platform."""
from __future__ import annotations
def fleet_prismic_status(repos: list[dict]) -> dict:
    active = [r for r in repos if r.get("active", True)]
    documents = sum(r.get("documents", 0) for r in repos)
    slices = sum(r.get("slices", 0) for r in repos)
    return {"repos": len(repos), "active": len(active), "documents": documents,
            "slices": slices, "all_active": len(active) == len(repos)}
