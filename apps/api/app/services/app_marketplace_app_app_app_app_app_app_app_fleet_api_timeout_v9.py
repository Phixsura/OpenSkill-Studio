"""Fleet API Timeout v9 — track API timeout configuration and violations."""
from __future__ import annotations
def fleet_api_timeout_v9(endpoints: list[dict]) -> dict:
    configured = [e for e in endpoints if e.get("timeout_configured")]
    timeouts_today = sum(e.get("timeouts_today", 0) for e in endpoints)
    avg_timeout = sum(e.get("timeout_ms", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    return {"endpoints": len(endpoints), "configured": len(configured), "timeouts_today": timeouts_today,
            "avg_timeout_ms": round(avg_timeout, 1), "healthy": timeouts_today < 10}
