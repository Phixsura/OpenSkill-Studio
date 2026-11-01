"""Fleet Custom Metric v9 — track user-defined custom metrics."""
from __future__ import annotations
def fleet_custom_metric_v9(metrics: list[dict]) -> dict:
    active = [m for m in metrics if m.get("active")]
    alerting = [m for m in metrics if m.get("has_alert")]
    data_points = sum(m.get("data_points_per_min", 0) for m in metrics)
    return {"metrics": len(metrics), "active": len(active), "alerting": len(alerting),
            "data_points_per_min": data_points, "healthy": True}
