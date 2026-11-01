"""Fleet HTMX — track hypermedia-driven UI apps."""
from __future__ import annotations
def fleet_htmx_status(apps: list[dict]) -> dict:
    active = [a for a in apps if a.get("active", True)]
    total_swaps = sum(a.get("swaps_24h", 0) for a in apps)
    avg_swap_ms = round(sum(a.get("avg_swap_ms", 0) for a in apps) / max(len(apps), 1), 1)
    return {"apps": len(apps), "active": len(active), "swaps_24h": total_swaps,
            "avg_swap_ms": avg_swap_ms, "snappy": avg_swap_ms < 100}
