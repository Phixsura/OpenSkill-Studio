"""Developer dashboard builder — compile complete dashboard view."""

from app.services.app_developer_stats import compute_developer_stats
from app.services.app_developer_onboarding import get_onboarding_progress


def build_developer_dashboard(*, developer: dict, apps: list[dict], completed_steps: set[str],
                                total_installs: int = 0, total_executions: int = 0, avg_health: float = 100.0) -> dict:
    stats = compute_developer_stats(
        app_count=len(apps), published_count=sum(1 for a in apps if a.get("status") == "published"),
        total_installs=total_installs, total_executions=total_executions, avg_health_score=avg_health,
    )
    onboarding = get_onboarding_progress(completed_steps)
    
    return {
        "developer": {"name": developer.get("display_name"), "verified": developer.get("verified", False)},
        "stats": stats,
        "onboarding": onboarding,
        "is_new": onboarding["completed_steps"] < 3,
        "recent_apps": apps[:5],
    }
