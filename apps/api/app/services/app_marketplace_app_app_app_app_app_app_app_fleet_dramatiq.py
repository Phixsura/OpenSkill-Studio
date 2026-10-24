"""Fleet Dramatiq — track Python actor task processing."""
from __future__ import annotations
def fleet_dramatiq_status(brokers: list[dict]) -> dict:
    online = [b for b in brokers if b.get("online", True)]
    total_msgs = sum(b.get("messages_24h", 0) for b in brokers)
    total_workers = sum(b.get("workers", 0) for b in brokers)
    return {"brokers": len(brokers), "online": len(online), "messages_24h": total_msgs,
            "workers": total_workers, "all_online": len(online) == len(brokers)}
