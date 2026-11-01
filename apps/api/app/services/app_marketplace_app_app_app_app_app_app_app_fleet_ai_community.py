"""Fleet AI Community Forum — track developer community engagement."""
from __future__ import annotations
def fleet_ai_community(forums: list[dict]) -> dict:
    active = [f for f in forums if f.get("active", True)]
    members = sum(f.get("members", 0) for f in forums)
    posts_24h = sum(f.get("posts_24h", 0) for f in forums)
    resolved_pct = round(sum(f.get("resolved_pct", 0) for f in forums) / max(len(forums), 1), 1)
    return {"forums": len(forums), "active": len(active), "members": members,
            "posts_24h": posts_24h, "resolved_pct": resolved_pct, "thriving": members > 1000}
