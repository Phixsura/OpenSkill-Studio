"""Fleet VPA — track vertical pod autoscaler recommendations."""
from __future__ import annotations
def fleet_vpa_status(vpas: list[dict]) -> dict:
    providing = [v for v in vpas if v.get("providing_recommendations", True)]
    applied = [v for v in vpas if v.get("mode") == "Auto"]
    savings = sum(v.get("monthly_savings_usd", 0) for v in vpas)
    return {"total": len(vpas), "providing": len(providing), "auto_mode": len(applied),
            "monthly_savings": round(savings, 2), "effective": savings > 0}
