"""App detail enricher — add computed fields to app data for display."""

from app.services.app_health_monitor import HealthScore


def enrich_app_detail(app: dict, *, executions: int = 0, errors: int = 0,
                       timeouts: int = 0, install_count: int = 0) -> dict:
    health = HealthScore(executions, errors, timeouts)
    return {
        **app,
        "health_score": health.score,
        "health_status": health.status,
        "error_rate": health.error_rate,
        "install_count": install_count,
        "has_sandbox": "sandbox" in app.get("manifest", {}),
        "has_ui": bool(app.get("manifest", {}).get("ui_extensions")),
        "permission_count": len(app.get("manifest", {}).get("permissions", [])),
    }
