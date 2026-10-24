"""Fleet Cilium — track eBPF-based networking health."""
from __future__ import annotations
def fleet_cilium_status(agents: list[dict]) -> dict:
    ready = [a for a in agents if a.get("ready", True)]
    policy_enforced = [a for a in agents if a.get("policy_enforcement", False)]
    return {"agents": len(agents), "ready": len(ready), "not_ready": len(agents) - len(ready),
            "policy_enforced": len(policy_enforced), "healthy": len(ready) == len(agents)}
