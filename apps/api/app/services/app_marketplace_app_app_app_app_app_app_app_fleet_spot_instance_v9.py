"""Fleet Spot Instance v9 — track spot/preemptible instance management."""
from __future__ import annotations
def fleet_spot_instance_v9(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("status") == "running"]
    interrupted = [i for i in instances if i.get("interrupted")]
    savings = sum(i.get("savings_pct", 0) for i in instances) / len(instances) if instances else 0
    return {"instances": len(instances), "running": len(running), "interrupted": len(interrupted),
            "avg_savings_pct": round(savings, 1), "healthy": len(interrupted) < len(instances) * 0.1}
