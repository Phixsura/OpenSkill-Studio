"""Fleet Karpenter — track node provisioning efficiency."""
from __future__ import annotations
def fleet_karpenter_status(provisioners: list[dict]) -> dict:
    active = [p for p in provisioners if p.get("active", True)]
    nodes_launched = sum(p.get("nodes_launched_24h", 0) for p in provisioners)
    nodes_terminated = sum(p.get("nodes_terminated_24h", 0) for p in provisioners)
    savings = sum(p.get("savings_usd_24h", 0) for p in provisioners)
    return {"provisioners": len(provisioners), "active": len(active),
            "launched_24h": nodes_launched, "terminated_24h": nodes_terminated,
            "savings_24h": round(savings, 2)}
