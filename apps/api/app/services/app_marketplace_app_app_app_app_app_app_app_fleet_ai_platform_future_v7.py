"""Fleet AI Platform Future v7 — track next-gen AI platform capabilities."""
from __future__ import annotations
def fleet_ai_platform_future_v7(planners: list[dict]) -> dict:
    active = [p for p in planners if p.get("active", True)]
    capabilities = sum(p.get("capabilities", 0) for p in planners)
    research = sum(p.get("research", 0) for p in planners)
    prototypes = sum(p.get("prototypes", 0) for p in planners)
    return {"planners": len(planners), "active": len(active), "capabilities": capabilities,
            "research": research, "prototypes": prototypes, "forward_looking": prototypes > 0}
