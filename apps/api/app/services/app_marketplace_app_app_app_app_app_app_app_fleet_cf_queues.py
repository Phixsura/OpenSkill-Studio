"""Fleet CF Queues — track Cloudflare message queues."""
from __future__ import annotations
def fleet_cf_queues(queues: list[dict]) -> dict:
    active = [q for q in queues if q.get("active", True)]
    msgs_produced = sum(q.get("produced_24h", 0) for q in queues)
    msgs_consumed = sum(q.get("consumed_24h", 0) for q in queues)
    backlog = msgs_produced - msgs_consumed
    return {"queues": len(queues), "active": len(active), "produced_24h": msgs_produced,
            "consumed_24h": msgs_consumed, "backlog": max(backlog, 0), "caught_up": backlog <= 0}
