"""Fleet API GraphQL Subscription v9 — track GraphQL subscription connections."""
from __future__ import annotations
def fleet_api_graphql_subscription_v9(subs: list[dict]) -> dict:
    active = [s for s in subs if s.get("active")]
    connections = sum(s.get("connections", 0) for s in subs)
    messages_sec = sum(s.get("messages_per_sec", 0) for s in subs)
    return {"subscriptions": len(subs), "active": len(active), "connections": connections,
            "messages_per_sec": messages_sec, "healthy": True}
