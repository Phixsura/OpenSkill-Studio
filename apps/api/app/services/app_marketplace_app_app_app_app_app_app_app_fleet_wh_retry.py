"""Fleet webhook retry — track webhook retry effectiveness."""
from __future__ import annotations
def fleet_webhook_retry(endpoints: list[dict]) -> dict:
    total_retries = sum(e.get("retries", 0) for e in endpoints)
    recovered = sum(e.get("recovered_after_retry", 0) for e in endpoints)
    exhausted = sum(e.get("retries_exhausted", 0) for e in endpoints)
    return {"total_retries": total_retries, "recovered": recovered,
            "exhausted": exhausted, "recovery_rate": round(recovered / max(total_retries, 1) * 100, 1)}
