"""Fleet API Retry v9 — track client-side retry behavior and patterns."""
from __future__ import annotations
def fleet_api_retry_v9(endpoints: list[dict]) -> dict:
    retried = sum(e.get("retries_today", 0) for e in endpoints)
    succeeded_after_retry = sum(e.get("succeeded_after_retry", 0) for e in endpoints)
    exhausted = sum(e.get("retries_exhausted", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "retries_today": retried,
            "succeeded_after_retry": succeeded_after_retry, "exhausted": exhausted,
            "healthy": exhausted == 0}
