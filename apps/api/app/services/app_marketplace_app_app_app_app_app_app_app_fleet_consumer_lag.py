"""Fleet consumer lag — track message queue consumer group lag."""
from __future__ import annotations
def fleet_consumer_lag(groups: list[dict]) -> dict:
    total_lag = sum(g.get("lag", 0) for g in groups)
    max_lag = max((g.get("lag", 0) for g in groups), default=0)
    behind = [g for g in groups if g.get("lag", 0) > 10000]
    return {"groups": len(groups), "total_lag": total_lag, "max_lag": max_lag,
            "behind": len(behind), "caught_up": max_lag < 1000}
