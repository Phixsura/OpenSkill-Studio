"""Fleet rate limiter effectiveness — measure protection quality."""
from __future__ import annotations
def fleet_rl_effectiveness(stats: dict) -> dict:
    total_requests = stats.get("total_requests", 0)
    blocked = stats.get("blocked", 0)
    false_positives = stats.get("false_positives", 0)
    precision = round((blocked - false_positives) / max(blocked, 1) * 100, 1)
    return {"total_requests": total_requests, "blocked": blocked,
            "false_positives": false_positives, "precision_pct": precision, "effective": precision >= 95}
