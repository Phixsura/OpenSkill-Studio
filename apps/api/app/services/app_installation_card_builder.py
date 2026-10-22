"""Installation card builder — build card data for installed apps."""


def build_installation_card(*, installation: dict, app: dict, health_score: int = 100) -> dict:
    return {
        "installation_id": installation.get("id"),
        "app_name": app.get("name"), "app_slug": app.get("slug"),
        "category": app.get("category"), "status": installation.get("status"),
        "version": installation.get("version"),
        "health_score": health_score,
        "health_status": "healthy" if health_score >= 95 else "degraded" if health_score >= 80 else "critical",
        "installed_at": installation.get("created_at"),
    }
