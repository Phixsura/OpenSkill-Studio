"""Fleet AI Router — track intelligent model routing."""
from __future__ import annotations
def fleet_ai_router(routers: list[dict]) -> dict:
    active = [r for r in routers if r.get("active", True)]
    requests_24h = sum(r.get("requests_24h", 0) for r in routers)
    models_routed = sum(r.get("models", 0) for r in routers)
    fallback_rate = round(sum(r.get("fallback_pct", 0) for r in routers) / max(len(routers), 1), 1)
    return {"routers": len(routers), "active": len(active), "requests_24h": requests_24h,
            "models": models_routed, "fallback_pct": fallback_rate}
