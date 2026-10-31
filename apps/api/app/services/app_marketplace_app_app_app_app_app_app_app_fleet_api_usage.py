"""Fleet API usage analytics — track API call patterns."""
from __future__ import annotations
def fleet_api_usage(endpoints: list[dict]) -> dict:
    total_calls = sum(e.get("calls_24h", 0) for e in endpoints)
    top = max(endpoints, key=lambda e: e.get("calls_24h", 0)) if endpoints else None
    unused = [e for e in endpoints if e.get("calls_24h", 0) == 0]
    return {"total_calls": total_calls, "endpoints": len(endpoints), "unused": len(unused),
            "top_endpoint": top.get("name") if top else None}
