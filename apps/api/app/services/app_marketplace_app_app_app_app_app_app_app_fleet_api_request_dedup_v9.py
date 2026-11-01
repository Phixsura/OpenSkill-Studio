"""Fleet API Request Dedup v9 — track request deduplication."""
from __future__ import annotations
def fleet_api_request_dedup_v9(endpoints: list[dict]) -> dict:
    dedup_enabled = [e for e in endpoints if e.get("dedup_enabled")]
    duplicates_caught = sum(e.get("duplicates_caught", 0) for e in endpoints)
    total_requests = sum(e.get("total_requests", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "dedup_enabled": len(dedup_enabled),
            "duplicates_caught": duplicates_caught, "total_requests": total_requests, "healthy": True}
