"""Fleet AI Outbox Processor — track transactional outbox pattern."""
from __future__ import annotations
def fleet_ai_outbox(processors: list[dict]) -> dict:
    active = [p for p in processors if p.get("active", True)]
    messages_24h = sum(p.get("messages_24h", 0) for p in processors)
    pending = sum(p.get("pending", 0) for p in processors)
    published = sum(p.get("published", 0) for p in processors)
    return {"processors": len(processors), "active": len(active), "messages_24h": messages_24h,
            "pending": pending, "published": published, "caught_up": pending < 100}
