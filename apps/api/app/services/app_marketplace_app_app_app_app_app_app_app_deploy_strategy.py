"""Deployment strategy selector — choose and configure deploy strategies."""
from __future__ import annotations

STRATEGIES = {
    "rolling": {"description": "Replace instances gradually", "downtime": False,
                "rollback_speed": "fast", "complexity": "low"},
    "blue_green": {"description": "Switch between two identical environments", "downtime": False,
                   "rollback_speed": "instant", "complexity": "medium"},
    "canary": {"description": "Route small traffic to new version", "downtime": False,
               "rollback_speed": "instant", "complexity": "high"},
    "recreate": {"description": "Stop old, start new", "downtime": True,
                 "rollback_speed": "slow", "complexity": "low"},
}


def recommend_strategy(requirements: dict) -> dict:
    needs_zero_downtime = requirements.get("zero_downtime", True)
    needs_fast_rollback = requirements.get("fast_rollback", True)
    has_traffic_splitting = requirements.get("traffic_splitting", False)
    if has_traffic_splitting:
        pick = "canary"
    elif needs_zero_downtime and needs_fast_rollback:
        pick = "blue_green"
    elif needs_zero_downtime:
        pick = "rolling"
    else:
        pick = "recreate"
    return {"recommended": pick, **STRATEGIES[pick], "all_strategies": list(STRATEGIES.keys())}


def compare_strategies(a: str, b: str) -> dict:
    sa = STRATEGIES.get(a, {})
    sb = STRATEGIES.get(b, {})
    return {"strategy_a": {"name": a, **sa}, "strategy_b": {"name": b, **sb},
            "prefer_a_when": "simpler setup needed" if sa.get("complexity") == "low" else "advanced features needed",
            "prefer_b_when": "simpler setup needed" if sb.get("complexity") == "low" else "advanced features needed"}
