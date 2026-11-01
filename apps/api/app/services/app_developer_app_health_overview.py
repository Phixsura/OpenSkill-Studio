"""App health overview — compile health data across all developer apps."""


def build_health_overview(apps_health: list[dict]) -> dict:
    if not apps_health:
        return {"total": 0, "healthy": 0, "degraded": 0, "critical": 0, "avg_score": 100, "worst_app": None}
    
    scores = [a.get("health_score", 100) for a in apps_health]
    healthy = sum(1 for s in scores if s >= 95)
    degraded = sum(1 for s in scores if 80 <= s < 95)
    critical = sum(1 for s in scores if s < 80)
    worst = min(apps_health, key=lambda a: a.get("health_score", 100))
    
    return {
        "total": len(apps_health),
        "healthy": healthy, "degraded": degraded, "critical": critical,
        "avg_score": round(sum(scores) / len(scores), 1),
        "worst_app": {"name": worst.get("name"), "score": worst.get("health_score")},
    }
