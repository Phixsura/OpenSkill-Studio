"""Fleet user engagement — track platform engagement metrics."""
from __future__ import annotations
def fleet_user_engagement(metrics: dict) -> dict:
    dau = metrics.get("dau", 0)
    mau = metrics.get("mau", 1)
    stickiness = round(dau / max(mau, 1) * 100, 1)
    avg_session = metrics.get("avg_session_min", 0)
    return {"dau": dau, "mau": mau, "stickiness_pct": stickiness,
            "avg_session_min": avg_session, "engaged": stickiness >= 20}
