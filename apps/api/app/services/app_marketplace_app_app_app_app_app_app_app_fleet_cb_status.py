"""Fleet circuit breaker status — track circuit breaker states."""
from __future__ import annotations
def fleet_cb_status(breakers: list[dict]) -> dict:
    open_cb = [b for b in breakers if b.get("state") == "open"]
    half_open = [b for b in breakers if b.get("state") == "half-open"]
    return {"total": len(breakers), "open": len(open_cb), "half_open": len(half_open),
            "closed": len(breakers) - len(open_cb) - len(half_open), "healthy": len(open_cb) == 0}
