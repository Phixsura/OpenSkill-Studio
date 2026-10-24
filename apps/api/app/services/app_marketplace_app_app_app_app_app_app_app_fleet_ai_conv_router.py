"""Fleet AI Conversation Router — track multi-model conversation routing."""
from __future__ import annotations
def fleet_ai_conversation_router(routers: list[dict]) -> dict:
    active = [r for r in routers if r.get("active", True)]
    conversations_24h = sum(r.get("conversations_24h", 0) for r in routers)
    models = sum(r.get("models", 0) for r in routers)
    optimal_route_pct = round(sum(r.get("optimal_pct", 0) for r in routers) / max(len(routers), 1), 1)
    return {"routers": len(routers), "active": len(active), "conversations_24h": conversations_24h,
            "models": models, "optimal_pct": optimal_route_pct, "smart": optimal_route_pct > 85}
