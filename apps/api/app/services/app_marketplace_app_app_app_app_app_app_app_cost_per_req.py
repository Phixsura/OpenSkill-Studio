"""Cost per request calculator — measure unit economics of API calls."""
from __future__ import annotations


def calculate_cost_per_request(total_cost: float, total_requests: int) -> dict:
    cpr = round(total_cost / max(total_requests, 1) * 1000, 4)  # cost per 1K requests
    return {"total_cost": total_cost, "total_requests": total_requests,
            "cost_per_1k": cpr, "cost_per_million": round(cpr * 1000, 2),
            "display_cpr": f"${cpr:.4f}/1K"}


def compare_cost_efficiency(current: dict, previous: dict) -> dict:
    delta = round(current["cost_per_1k"] - previous["cost_per_1k"], 4)
    pct = round(delta / max(abs(previous["cost_per_1k"]), 0.0001) * 100, 1)
    return {"current_cpr": current["cost_per_1k"], "previous_cpr": previous["cost_per_1k"],
            "delta": delta, "pct_change": pct,
            "improving": delta < 0}
