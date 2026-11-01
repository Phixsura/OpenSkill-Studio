"""Fleet AI Total Cost v2 — track total cost of ownership for AI platform."""
from __future__ import annotations
def fleet_ai_total_cost_v2(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    compute_usd = round(sum(t.get("compute", 0) for t in trackers), 2)
    storage_usd = round(sum(t.get("storage", 0) for t in trackers), 2)
    network_usd = round(sum(t.get("network", 0) for t in trackers), 2)
    total = compute_usd + storage_usd + network_usd
    return {"trackers": len(trackers), "active": len(active), "compute": compute_usd,
            "storage": storage_usd, "network": network_usd, "total": total, "tracked": total > 0}
