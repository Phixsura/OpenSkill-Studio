"""Fleet Session Store v9 — track user session persistence and expiry."""
from __future__ import annotations
def fleet_session_store_v9(sessions: list[dict]) -> dict:
    active = [s for s in sessions if s.get("active")]
    expired = [s for s in sessions if s.get("expired")]
    avg_ttl = sum(s.get("ttl_min", 0) for s in sessions) / len(sessions) if sessions else 0
    return {"total": len(sessions), "active": len(active), "expired": len(expired),
            "avg_ttl_min": round(avg_ttl, 1), "healthy": len(expired) < len(sessions) * 0.1}
