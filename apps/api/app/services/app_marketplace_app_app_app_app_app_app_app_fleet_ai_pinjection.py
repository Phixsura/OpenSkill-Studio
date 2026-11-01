"""Fleet AI Prompt Injection Defense — track injection attack prevention."""
from __future__ import annotations
def fleet_ai_pinjection(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    scanned_24h = sum(s.get("scanned_24h", 0) for s in services)
    blocked_24h = sum(s.get("blocked_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "scanned_24h": scanned_24h,
            "blocked_24h": blocked_24h, "block_rate": round(blocked_24h / max(scanned_24h, 1) * 100, 2)}
