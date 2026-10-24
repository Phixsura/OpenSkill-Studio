"""Fleet AI Retry Policy — track AI request retry and backoff strategies."""
from __future__ import annotations
def fleet_ai_retry_policy(policies: list[dict]) -> dict:
    active = [p for p in policies if p.get("active", True)]
    retries_24h = sum(p.get("retries_24h", 0) for p in policies)
    success_after_retry = sum(p.get("success_retries", 0) for p in policies)
    max_attempts = max((p.get("max_attempts", 0) for p in policies), default=0)
    return {"policies": len(policies), "active": len(active), "retries_24h": retries_24h,
            "success_retries": success_after_retry, "max_attempts": max_attempts, "resilient": success_after_retry > 0}
