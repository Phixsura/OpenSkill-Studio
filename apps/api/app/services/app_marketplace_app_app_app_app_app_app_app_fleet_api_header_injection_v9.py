"""Fleet API Header Injection v9 — track header injection protection."""
from __future__ import annotations
def fleet_api_header_injection_v9(endpoints: list[dict]) -> dict:
    protected = [e for e in endpoints if e.get("header_injection_protected")]
    blocked = sum(e.get("blocked_today", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "protected": len(protected), "blocked_today": blocked,
            "healthy": len(protected) == len(endpoints)}
