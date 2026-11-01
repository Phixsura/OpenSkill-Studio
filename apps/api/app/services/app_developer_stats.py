"""Developer stats — aggregate stats for a developer account."""


def compute_developer_stats(
    *,
    app_count: int = 0,
    published_count: int = 0,
    total_installs: int = 0,
    total_executions: int = 0,
    avg_health_score: float = 100.0,
) -> dict:
    """Compute developer dashboard statistics."""
    return {
        "app_count": app_count,
        "published_count": published_count,
        "draft_count": app_count - published_count,
        "total_installs": total_installs,
        "total_executions": total_executions,
        "avg_health_score": round(avg_health_score, 1),
        "publish_rate": round(published_count / app_count * 100, 1) if app_count > 0 else 0,
    }
