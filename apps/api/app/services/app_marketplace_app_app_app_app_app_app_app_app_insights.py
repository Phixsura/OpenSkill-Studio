"""App insights dashboard — unified view of app performance metrics."""
from __future__ import annotations


def build_insights(*, app_id: str, installs_7d: int, api_calls_7d: int,
                     errors_7d: int, avg_rating: float, reviews_7d: int,
                     active_users: int, churn_pct: float) -> dict:
    error_rate = round(errors_7d / max(api_calls_7d, 1) * 100, 2)
    health = "excellent" if error_rate < 0.5 and avg_rating >= 4.5 else \
             "good" if error_rate < 2 and avg_rating >= 4.0 else \
             "needs_attention" if error_rate < 5 else "critical"
    return {
        "app_id": app_id,
        "kpis": [
            {"label": "Installs (7d)", "value": installs_7d, "display": f"+{installs_7d:,}", "trend": "up" if installs_7d > 0 else "flat"},
            {"label": "API Calls (7d)", "value": api_calls_7d, "display": f"{api_calls_7d:,}"},
            {"label": "Error Rate", "value": error_rate, "display": f"{error_rate}%"},
            {"label": "Avg Rating", "value": avg_rating, "display": f"{avg_rating} ⭐"},
            {"label": "Active Users", "value": active_users, "display": f"{active_users:,}"},
            {"label": "Churn", "value": churn_pct, "display": f"{churn_pct}%"},
        ],
        "health": health, "error_rate": error_rate,
    }
