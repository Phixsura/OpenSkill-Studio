"""Fleet API idempotency — track idempotency key usage."""
from __future__ import annotations
def fleet_idempotency(endpoints: list[dict]) -> dict:
    with_key = [e for e in endpoints if e.get("supports_idempotency", False)]
    replayed = sum(e.get("replay_count", 0) for e in endpoints)
    return {"total": len(endpoints), "with_idempotency": len(with_key),
            "replayed_requests": replayed, "coverage_pct": round(len(with_key) / max(len(endpoints), 1) * 100, 1)}
