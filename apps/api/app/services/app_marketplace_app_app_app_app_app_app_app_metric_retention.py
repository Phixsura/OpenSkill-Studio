"""Metric retention policy — manage metric data retention."""
from __future__ import annotations


RETENTION_TIERS = {
    "raw": {"resolution": "1s", "retention_days": 7, "cost_factor": 1.0},
    "1min": {"resolution": "1m", "retention_days": 30, "cost_factor": 0.1},
    "5min": {"resolution": "5m", "retention_days": 90, "cost_factor": 0.02},
    "1hour": {"resolution": "1h", "retention_days": 365, "cost_factor": 0.003},
}


def calculate_storage(metrics_count: int, data_points_per_day: int) -> dict:
    tiers = {}
    total_gb = 0
    for tier, config in RETENTION_TIERS.items():
        points = data_points_per_day * config["retention_days"] * metrics_count
        size_gb = round(points * 8 / 1e9 * config["cost_factor"], 2)  # 8 bytes per point
        total_gb += size_gb
        tiers[tier] = {"retention_days": config["retention_days"], "size_gb": size_gb,
                        "resolution": config["resolution"]}
    return {"tiers": tiers, "total_gb": round(total_gb, 2), "metrics_count": metrics_count}


def optimize_retention(current_gb: float, target_gb: float) -> dict:
    reduction_needed = max(0, current_gb - target_gb)
    pct = round(reduction_needed / max(current_gb, 0.01) * 100)
    return {"current_gb": current_gb, "target_gb": target_gb,
            "reduction_gb": round(reduction_needed, 2), "reduction_pct": pct,
            "needs_optimization": reduction_needed > 0}
