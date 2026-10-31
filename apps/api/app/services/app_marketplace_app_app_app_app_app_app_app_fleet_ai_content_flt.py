"""Fleet AI Content Filter — track AI content moderation and safety."""
from __future__ import annotations
def fleet_ai_content_filter(filters: list[dict]) -> dict:
    active = [f for f in filters if f.get("active", True)]
    scanned_24h = sum(f.get("scanned_24h", 0) for f in filters)
    blocked_24h = sum(f.get("blocked_24h", 0) for f in filters)
    block_rate = round(blocked_24h / max(scanned_24h, 1) * 100, 2)
    return {"filters": len(filters), "active": len(active), "scanned_24h": scanned_24h,
            "blocked_24h": blocked_24h, "block_rate": block_rate, "protecting": len(active) == len(filters)}
