"""Fleet spot instance usage — track spot vs on-demand ratio."""
from __future__ import annotations
def fleet_spot_usage(nodes: list[dict]) -> dict:
    spot = [n for n in nodes if n.get("type") == "spot"]
    on_demand = [n for n in nodes if n.get("type") == "on-demand"]
    pct = round(len(spot) / max(len(nodes), 1) * 100, 1)
    return {"total": len(nodes), "spot": len(spot), "on_demand": len(on_demand),
            "spot_pct": pct, "cost_optimized": pct >= 50}
