"""Webhook retry config — configurable retry policies per webhook."""
from __future__ import annotations

RETRY_POLICIES = {
    "aggressive": {"max_retries": 10, "base_delay_ms": 1000, "max_delay_ms": 60000, "strategy": "exponential"},
    "standard": {"max_retries": 5, "base_delay_ms": 5000, "max_delay_ms": 300000, "strategy": "exponential"},
    "conservative": {"max_retries": 3, "base_delay_ms": 30000, "max_delay_ms": 3600000, "strategy": "exponential"},
    "none": {"max_retries": 0, "base_delay_ms": 0, "max_delay_ms": 0, "strategy": "none"},
}


def get_policy(name: str) -> dict:
    policy = RETRY_POLICIES.get(name, RETRY_POLICIES["standard"])
    return {"name": name, **policy}


def compute_retry_schedule(policy_name: str) -> list[dict]:
    policy = RETRY_POLICIES.get(policy_name, RETRY_POLICIES["standard"])
    schedule = []
    delay = policy["base_delay_ms"]
    for i in range(1, policy["max_retries"] + 1):
        schedule.append({"attempt": i, "delay_ms": min(delay, policy["max_delay_ms"]),
                          "delay_display": f"{min(delay, policy['max_delay_ms']) / 1000:.0f}s"})
        delay *= 2
    return schedule


def list_policies() -> list[dict]:
    return [{"name": k, **v} for k, v in RETRY_POLICIES.items()]
