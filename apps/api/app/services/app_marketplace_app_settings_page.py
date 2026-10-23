"""App settings page — complete settings page combining all app configuration."""


def build_app_settings_page(*, app: dict, config: dict, api_keys: list[dict],
                                webhooks: list[dict], team: list[dict], env_vars: list[dict],
                                domains: list[dict]) -> dict:
    return {
        "page_type": "app_settings",
        "app": {"id": app["id"], "name": app["name"], "slug": app.get("slug"), "status": app.get("status")},
        "tabs": [
            {"key": "general", "title": "General", "icon": "⚙️", "data": {
                "name": app["name"], "slug": app.get("slug"), "category": app.get("category"),
                "description": app.get("description", ""), "status": app.get("status")}},
            {"key": "api_keys", "title": f"API Keys ({len(api_keys)})", "icon": "🔑",
             "data": {"keys": [{"name": k["name"], "prefix": k.get("prefix")} for k in api_keys]}},
            {"key": "webhooks", "title": f"Webhooks ({len(webhooks)})", "icon": "🔗",
             "data": {"endpoints": webhooks}},
            {"key": "team", "title": f"Team ({len(team)})", "icon": "👥",
             "data": {"members": team}},
            {"key": "env_vars", "title": f"Environment ({len(env_vars)})", "icon": "📝",
             "data": {"variables": env_vars}},
            {"key": "domains", "title": f"Domains ({len(domains)})", "icon": "🌐",
             "data": {"domains": domains}},
            {"key": "danger", "title": "Danger Zone", "icon": "⚠️",
             "data": {"actions": ["transfer", "archive", "delete"]}},
        ],
        "tab_count": 7,
    }
