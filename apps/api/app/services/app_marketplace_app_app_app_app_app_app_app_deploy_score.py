"""Deployment scorecard — grade deployment practices."""
from __future__ import annotations


def score_deployments(metrics: dict) -> dict:
    frequency = min(metrics.get("deploys_per_week", 0) / 10 * 100, 100)
    success_rate = metrics.get("success_rate_pct", 0)
    rollback_rate = max(0, 100 - metrics.get("rollback_pct", 0) * 5)
    auto_pct = metrics.get("automated_pct", 0)
    approval_time = max(0, 100 - metrics.get("avg_approval_hours", 0) * 4)
    
    total = round((frequency * 0.2 + success_rate * 0.3 + rollback_rate * 0.15 +
                    auto_pct * 0.2 + approval_time * 0.15))
    grade = "A" if total >= 90 else "B" if total >= 75 else "C" if total >= 60 else "D"
    return {"total_score": total, "grade": grade,
            "breakdown": {"frequency": round(frequency), "success_rate": round(success_rate),
                           "rollback_rate": round(rollback_rate), "automation": round(auto_pct),
                           "approval_time": round(approval_time)}}
