"""App settings builder — compile settings page data."""

def build_app_settings(app: dict) -> dict:
    return {
        "general": {"name": app.get("name"), "slug": app.get("slug"), "description": app.get("description"),
                     "category": app.get("category"), "visibility": app.get("visibility", "private")},
        "oauth": {"client_id": app.get("oauth_client_id"), "redirect_uris": app.get("redirect_uris", [])},
        "webhook": {"url": app.get("webhook_url"), "configured": bool(app.get("webhook_url"))},
        "danger_zone": {"can_delete": app.get("status") == "draft", "can_archive": app.get("status") in ("published", "deprecated")},
    }
