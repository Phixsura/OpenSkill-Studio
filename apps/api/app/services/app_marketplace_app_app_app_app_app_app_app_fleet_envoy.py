"""Fleet Envoy — track Envoy proxy sidecar health."""
from __future__ import annotations
def fleet_envoy_status(proxies: list[dict]) -> dict:
    live = [p for p in proxies if p.get("live", True)]
    draining = [p for p in proxies if p.get("draining", False)]
    total_rps = sum(p.get("rps", 0) for p in proxies)
    return {"total": len(proxies), "live": len(live), "draining": len(draining),
            "total_rps": total_rps, "all_live": len(live) == len(proxies)}
