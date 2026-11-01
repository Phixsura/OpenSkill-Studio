"""Fleet API Quota Enforcement v9 — track quota enforcement per consumer."""
from __future__ import annotations
def fleet_api_quota_enforcement_v9(consumers: list[dict]) -> dict:
    enforced = [c for c in consumers if c.get("quota_enforced")]
    exceeded = [c for c in consumers if c.get("quota_exceeded")]
    total_calls = sum(c.get("calls_today", 0) for c in consumers)
    return {"consumers": len(consumers), "enforced": len(enforced), "exceeded": len(exceeded),
            "calls_today": total_calls, "healthy": len(exceeded) == 0}
