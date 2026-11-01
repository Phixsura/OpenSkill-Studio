"""Fleet Spacelift — track IaC management platform."""
from __future__ import annotations
def fleet_spacelift_status(stacks: list[dict]) -> dict:
    tracked = [s for s in stacks if s.get("tracked", True)]
    drifted = [s for s in stacks if s.get("drifted", False)]
    policies = sum(s.get("policies", 0) for s in stacks)
    return {"total": len(stacks), "tracked": len(tracked), "drifted": len(drifted),
            "policies": policies, "clean": len(drifted) == 0}
