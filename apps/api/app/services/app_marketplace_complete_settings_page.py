"""Complete settings page — aggregate all app settings into one view."""


def build_complete_settings_page(*, app: dict, api_keys: list[dict], webhooks: list[dict],
                                    team_members: list[dict], config: dict) -> dict:
    return {
        "page_type": "app_settings",
        "app": {"id": app["id"], "name": app["name"], "status": app.get("status")},
        "sections": [
            {"key": "general", "title": "General", "icon": "⚙️", "data": {
                "name": app["name"], "description": app.get("description", ""),
                "category": app.get("category"), "status": app.get("status"),
            }},
            {"key": "api_keys", "title": f"API Keys ({len(api_keys)})", "icon": "🔑",
             "data": {"keys": [{"name": k["name"], "prefix": k.get("prefix")} for k in api_keys]}},
            {"key": "webhooks", "title": f"Webhooks ({len(webhooks)})", "icon": "🔗",
             "data": {"endpoints": [{"url": w.get("url"), "active": w.get("active")} for w in webhooks]}},
            {"key": "team", "title": f"Team ({len(team_members)})", "icon": "👥",
             "data": {"members": team_members}},
            {"key": "config", "title": "Configuration", "icon": "📝", "data": config},
        ],
    }
