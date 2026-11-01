"""Fleet Retry Policy v9 — track retry strategies and backoff patterns."""
from __future__ import annotations
def fleet_retry_policy_v9(policies: list[dict]) -> dict:
    exponential = [p for p in policies if p.get("strategy") == "exponential"]
    linear = [p for p in policies if p.get("strategy") == "linear"]
    retries_today = sum(p.get("retries_today", 0) for p in policies)
    return {"policies": len(policies), "exponential": len(exponential), "linear": len(linear),
            "retries_today": retries_today, "healthy": True}
