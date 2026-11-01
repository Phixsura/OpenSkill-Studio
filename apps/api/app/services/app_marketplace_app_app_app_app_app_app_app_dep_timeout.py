"""Dependency timeout calculator — calculate cascading timeouts for service chains."""
from __future__ import annotations


def calculate_chain_timeout(chain: list[dict], buffer_pct: float = 10) -> dict:
    total_ms = sum(s.get("timeout_ms", 0) for s in chain)
    buffer_ms = round(total_ms * buffer_pct / 100)
    recommended = total_ms + buffer_ms
    steps = []
    cumulative = 0
    for s in chain:
        t = s.get("timeout_ms", 0)
        cumulative += t
        steps.append({"service": s["service"], "timeout_ms": t,
                       "cumulative_ms": cumulative})
    return {"chain_timeout_ms": recommended, "sum_ms": total_ms,
            "buffer_ms": buffer_ms, "steps": steps, "depth": len(chain)}


def validate_timeouts(parent_timeout: int, child_timeouts: list[dict]) -> dict:
    child_sum = sum(c.get("timeout_ms", 0) for c in child_timeouts)
    valid = child_sum < parent_timeout
    slack = parent_timeout - child_sum
    return {"valid": valid, "parent_ms": parent_timeout,
            "children_sum_ms": child_sum, "slack_ms": slack,
            "recommendation": "increase_parent" if not valid else "ok"}
