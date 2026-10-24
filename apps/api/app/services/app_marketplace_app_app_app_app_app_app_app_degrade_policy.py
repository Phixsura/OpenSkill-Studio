"""Service degradation policy — define degradation tiers and actions."""
from __future__ import annotations


def evaluate_degradation(load_pct: float, error_rate: float, latency_ms: float,
                          policies: list[dict]) -> dict:
    triggered = []
    for p in policies:
        conditions_met = True
        for cond in p.get("conditions", []):
            metric = cond["metric"]
            threshold = cond["threshold"]
            actual = {"load_pct": load_pct, "error_rate": error_rate, "latency_ms": latency_ms}.get(metric, 0)
            if cond["op"] == "gt" and actual <= threshold:
                conditions_met = False
        if conditions_met:
            triggered.append({"policy": p["name"], "tier": p.get("tier", "unknown"),
                              "actions": p.get("actions", [])})
    # Return highest tier
    tier_order = {"emergency": 0, "severe": 1, "moderate": 2, "minor": 3}
    triggered.sort(key=lambda t: tier_order.get(t["tier"], 99))
    active_tier = triggered[0]["tier"] if triggered else "normal"
    return {"active_tier": active_tier, "triggered": triggered,
            "actions": triggered[0]["actions"] if triggered else [],
            "degraded": len(triggered) > 0}
