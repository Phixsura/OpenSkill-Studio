"""Fleet AI GitOps Controller — track Git-driven AI infrastructure management."""
from __future__ import annotations
def fleet_ai_gitops(controllers: list[dict]) -> dict:
    active = [c for c in controllers if c.get("active", True)]
    repos = sum(c.get("repos", 0) for c in controllers)
    syncs_24h = sum(c.get("syncs_24h", 0) for c in controllers)
    out_of_sync = sum(c.get("out_of_sync", 0) for c in controllers)
    return {"controllers": len(controllers), "active": len(active), "repos": repos,
            "syncs_24h": syncs_24h, "out_of_sync": out_of_sync, "synced": out_of_sync == 0}
