"""App health score — composite quality metric for marketplace ranking."""


def compute_health_score(*, uptime_pct: float, error_rate: float, avg_response_ms: int,
                            review_avg: float, update_frequency_days: int) -> dict:
    # Each dimension 0-100
    uptime_score = min(100, uptime_pct)
    error_score = max(0, 100 - error_rate * 10)
    perf_score = max(0, 100 - (avg_response_ms - 100) / 10) if avg_response_ms > 100 else 100
    review_score = review_avg * 20  # 5.0 → 100
    freshness_score = max(0, 100 - update_frequency_days) if update_frequency_days < 100 else 0

    weights = {"uptime": 0.3, "errors": 0.2, "performance": 0.2, "reviews": 0.15, "freshness": 0.15}
    composite = (uptime_score * weights["uptime"] + error_score * weights["errors"] +
                 perf_score * weights["performance"] + review_score * weights["reviews"] +
                 freshness_score * weights["freshness"])
    grade = "A" if composite >= 90 else "B" if composite >= 75 else "C" if composite >= 60 else "D" if composite >= 40 else "F"
    return {
        "score": round(composite, 1), "grade": grade,
        "breakdown": {"uptime": round(uptime_score, 1), "errors": round(error_score, 1),
                       "performance": round(perf_score, 1), "reviews": round(review_score, 1),
                       "freshness": round(freshness_score, 1)},
    }
