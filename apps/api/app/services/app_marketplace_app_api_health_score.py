"""API health score — composite score for API reliability and performance."""


def compute_api_health_score(*, uptime_pct: float, avg_response_ms: int, error_rate: float,
                                documentation_coverage: float, deprecation_count: int) -> dict:
    scores = {
        "availability": min(100, uptime_pct),
        "performance": max(0, 100 - (avg_response_ms - 100) / 5) if avg_response_ms > 100 else 100,
        "reliability": max(0, 100 - error_rate * 20),
        "documentation": documentation_coverage,
        "stability": max(0, 100 - deprecation_count * 10),
    }
    weights = {"availability": 0.3, "performance": 0.2, "reliability": 0.25, "documentation": 0.1, "stability": 0.15}
    composite = sum(scores[k] * weights[k] for k in weights)
    grade = "A+" if composite >= 95 else "A" if composite >= 90 else "B" if composite >= 75 else "C" if composite >= 60 else "D" if composite >= 40 else "F"
    return {"score": round(composite, 1), "grade": grade, "breakdown": {k: round(v, 1) for k, v in scores.items()}}
