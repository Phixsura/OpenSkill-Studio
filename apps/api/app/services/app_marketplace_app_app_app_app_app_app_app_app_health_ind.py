"""App health indicator — compute app health from multiple signals."""
from __future__ import annotations


def compute_app_health(*, error_rate: float, avg_latency_ms: float,
                          uptime_pct: float, user_satisfaction: float,
                          crash_free_rate: float = 99.9) -> dict:
    score = 0
    checks = []
    # Error rate (0-25)
    er_score = 25 if error_rate < 0.5 else 15 if error_rate < 2 else 5 if error_rate < 5 else 0
    score += er_score
    checks.append({"metric": "Error Rate", "value": f"{error_rate}%", "score": er_score, "max": 25})
    # Latency (0-25)
    lt_score = 25 if avg_latency_ms < 200 else 15 if avg_latency_ms < 500 else 5
    score += lt_score
    checks.append({"metric": "Latency", "value": f"{avg_latency_ms}ms", "score": lt_score, "max": 25})
    # Uptime (0-25)
    up_score = 25 if uptime_pct >= 99.9 else 15 if uptime_pct >= 99 else 5
    score += up_score
    checks.append({"metric": "Uptime", "value": f"{uptime_pct}%", "score": up_score, "max": 25})
    # Satisfaction (0-25)
    sat_score = 25 if user_satisfaction >= 4.5 else 15 if user_satisfaction >= 4.0 else 5
    score += sat_score
    checks.append({"metric": "Satisfaction", "value": f"{user_satisfaction}⭐", "score": sat_score, "max": 25})
    grade = "A" if score >= 90 else "B" if score >= 70 else "C" if score >= 50 else "D"
    return {"score": score, "grade": grade, "display": f"{score}/100 ({grade})",
            "checks": checks}
