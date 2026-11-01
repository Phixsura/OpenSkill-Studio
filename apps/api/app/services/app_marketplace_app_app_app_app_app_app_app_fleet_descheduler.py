"""Fleet Descheduler — track pod rebalancing actions."""
from __future__ import annotations
def fleet_descheduler_status(actions: list[dict]) -> dict:
    evicted = sum(a.get("pods_evicted", 0) for a in actions)
    rebalanced = [a for a in actions if a.get("type") == "rebalance"]
    return {"total_actions": len(actions), "pods_evicted": evicted,
            "rebalances": len(rebalanced), "active": len(actions) > 0}
