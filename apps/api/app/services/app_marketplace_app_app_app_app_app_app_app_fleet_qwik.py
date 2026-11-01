"""Fleet Qwik — track resumable web framework health."""
from __future__ import annotations
def fleet_qwik_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    total_routes = sum(a.get("routes", 0) for a in apps)
    ttfb_ms = round(sum(a.get("ttfb_ms", 0) for a in apps) / max(len(apps), 1), 1)
    return {"apps": len(apps), "deployed": len(deployed), "routes": total_routes,
            "avg_ttfb_ms": ttfb_ms, "instant": ttfb_ms < 100}
