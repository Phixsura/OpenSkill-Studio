"""Fleet dark launch — track shadow traffic testing."""
from __future__ import annotations
def fleet_dark_launch(features: list[dict]) -> dict:
    active = [f for f in features if f.get("dark_launch", False)]
    total_shadow = sum(f.get("shadow_traffic_pct", 0) for f in active)
    return {"total": len(features), "dark_launching": len(active),
            "avg_shadow_pct": round(total_shadow / max(len(active), 1), 1)}
