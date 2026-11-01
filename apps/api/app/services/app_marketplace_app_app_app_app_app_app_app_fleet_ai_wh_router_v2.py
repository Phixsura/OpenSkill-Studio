"""Fleet AI Webhook Router v2 — track intelligent webhook routing."""
from __future__ import annotations
def fleet_ai_webhook_router_v2(routers: list[dict]) -> dict:
    active = [r for r in routers if r.get("active", True)]
    webhooks = sum(r.get("webhooks", 0) for r in routers)
    routed_24h = sum(r.get("routed_24h", 0) for r in routers)
    retry_success = round(sum(r.get("retry_success_pct", 0) for r in routers) / max(len(routers), 1), 1)
    return {"routers": len(routers), "active": len(active), "webhooks": webhooks,
            "routed_24h": routed_24h, "retry_success": retry_success, "reliable": retry_success > 95}
