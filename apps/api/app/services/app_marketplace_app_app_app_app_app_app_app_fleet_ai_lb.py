"""Fleet AI Load Balancer — track AI inference load distribution."""
from __future__ import annotations
def fleet_ai_lb(balancers: list[dict]) -> dict:
    active = [b for b in balancers if b.get("active", True)]
    total_rps = sum(b.get("rps", 0) for b in balancers)
    backends = sum(b.get("backends", 0) for b in balancers)
    return {"balancers": len(balancers), "active": len(active), "rps": total_rps,
            "backends": backends, "all_active": len(active) == len(balancers)}
