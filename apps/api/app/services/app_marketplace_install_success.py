"""Install success — post-install confirmation and next steps."""


def build_install_success(*, app: dict, installation_id: str, scopes_granted: list[str]) -> dict:
    next_steps = [
        {"step": 1, "title": "Configure Settings", "url": f"/apps/{installation_id}/settings", "icon": "⚙️"},
        {"step": 2, "title": "Set Up Webhooks", "url": f"/apps/{installation_id}/webhooks", "icon": "🔗"},
        {"step": 3, "title": "View Documentation", "url": f"/marketplace/apps/{app.get('slug')}/docs", "icon": "📚"},
    ]
    return {
        "success": True,
        "message": f"Successfully installed {app['name']}!",
        "installation_id": installation_id,
        "app": {"name": app["name"], "slug": app.get("slug"), "icon": app.get("icon")},
        "scopes_granted": scopes_granted,
        "next_steps": next_steps,
    }
