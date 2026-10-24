"""Fleet Postmark — track transactional email health."""
from __future__ import annotations
def fleet_postmark_status(servers: list[dict]) -> dict:
    active = [s for s in servers if s.get("active", True)]
    delivered = sum(s.get("delivered_24h", 0) for s in servers)
    bounce_rate = round(sum(s.get("bounce_rate", 0) for s in servers) / max(len(servers), 1), 2)
    return {"servers": len(servers), "active": len(active), "delivered_24h": delivered,
            "bounce_rate": bounce_rate, "reliable": bounce_rate < 2}
