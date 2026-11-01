"""Developer score — gamified developer reputation score."""


def calculate_developer_score(*, activity: dict) -> dict:
    weights = {
        "apps_published": 50,
        "total_installs": 0.01,
        "avg_rating": 20,
        "reviews_responded": 5,
        "docs_quality": 30,
        "security_clean": 40,
        "active_days_30": 2,
    }
    score = 0
    breakdown = {}
    for metric, weight in weights.items():
        value = activity.get(metric, 0)
        points = round(value * weight, 1)
        points = min(points, 200)  # cap per metric
        breakdown[metric] = points
        score += points
    total = min(round(score), 1000)
    tier = "legend" if total >= 800 else "expert" if total >= 500 else "rising" if total >= 200 else "newcomer"
    return {
        "score": total,
        "max_score": 1000,
        "tier": tier,
        "breakdown": breakdown,
        "percentile": min(round(total / 10), 99),
    }
