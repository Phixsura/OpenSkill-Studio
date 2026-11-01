"""Team performance tracker — measure team productivity and health."""
from __future__ import annotations


def track_team_performance(team: str, metrics: dict) -> dict:
    velocity = metrics.get("story_points", 0)
    cycle_time = metrics.get("avg_cycle_time_days", 0)
    deployment_freq = metrics.get("deploys_per_week", 0)
    incidents = metrics.get("incidents_caused", 0)
    pr_review_time = metrics.get("avg_pr_review_hours", 0)
    
    health_score = round(
        min(velocity / 50, 1) * 25 +
        max(0, 1 - cycle_time / 14) * 25 +
        min(deployment_freq / 5, 1) * 20 +
        max(0, 1 - incidents / 5) * 15 +
        max(0, 1 - pr_review_time / 24) * 15)
    
    return {"team": team, "velocity": velocity, "cycle_time_days": cycle_time,
            "deploys_per_week": deployment_freq, "incidents": incidents,
            "pr_review_hours": pr_review_time, "health_score": health_score,
            "rating": "excellent" if health_score >= 80 else "good" if health_score >= 60 else "needs_improvement"}
