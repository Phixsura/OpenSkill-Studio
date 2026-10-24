"""Fleet API throttle — monitor throttled requests per tenant."""
from __future__ import annotations
def fleet_throttle_monitor(tenants: list[dict]) -> dict:
    throttled = [t for t in tenants if t.get("throttled_pct", 0) > 0]
    heavy = [t for t in tenants if t.get("throttled_pct", 0) > 10]
    return {"total": len(tenants), "throttled": len(throttled), "heavy": len(heavy),
            "clean": len(throttled) == 0}
