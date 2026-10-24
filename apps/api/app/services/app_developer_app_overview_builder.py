"""App overview builder — compile complete app overview page data."""


def build_app_overview(*, app: dict, version: dict | None, stats: dict, health: dict,
                        permissions: list[str], badges: list[dict]) -> dict:
    return {
        "app": app,
        "current_version": version.get("version") if version else None,
        "review_status": version.get("review_status") if version else None,
        "stats": stats,
        "health": health,
        "permission_count": len(permissions),
        "badge_count": len(badges),
        "has_sandbox": bool(app.get("manifest", {}).get("sandbox")),
        "has_webhook": bool(app.get("webhook_url")),
        "has_ui_extensions": bool(app.get("manifest", {}).get("ui_extensions")),
    }
