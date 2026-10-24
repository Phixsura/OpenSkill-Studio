"""Fleet outbox pattern — track transactional outbox health."""
from __future__ import annotations
def fleet_outbox_status(tables: list[dict]) -> dict:
    pending = sum(t.get("pending_messages", 0) for t in tables)
    processed = sum(t.get("processed_24h", 0) for t in tables)
    stuck = [t for t in tables if t.get("oldest_pending_min", 0) > 60]
    return {"tables": len(tables), "pending": pending, "processed_24h": processed,
            "stuck": len(stuck), "healthy": len(stuck) == 0}
