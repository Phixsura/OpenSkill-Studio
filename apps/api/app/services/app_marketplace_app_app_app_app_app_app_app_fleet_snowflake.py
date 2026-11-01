"""Fleet Snowflake — track data cloud warehouse health."""
from __future__ import annotations
def fleet_snowflake_status(warehouses: list[dict]) -> dict:
    running = [w for w in warehouses if w.get("state") == "STARTED"]
    credits_used = sum(w.get("credits_24h", 0) for w in warehouses)
    queries_24h = sum(w.get("queries_24h", 0) for w in warehouses)
    return {"warehouses": len(warehouses), "running": len(running), "credits_24h": round(credits_used, 2),
            "queries_24h": queries_24h, "cost_controlled": credits_used < 100}
