"""App settings page — build the complete app settings data."""
from __future__ import annotations
import html


def build_app_settings(app: dict) -> dict:
    return {
        "app_name": html.escape(app.get("name", "")),
        "app_id": app.get("id", ""),
        "sections": [
            {"id": "general", "title": "General Settings", "icon": "⚙️",
             "fields": ["name", "description", "category", "icon_url"]},
            {"id": "webhooks", "title": "Webhooks", "icon": "🔗",
             "fields": ["endpoint_url", "events", "secret"]},
            {"id": "permissions", "title": "Permissions", "icon": "🔐",
             "fields": ["scopes", "redirect_uris"]},
            {"id": "deployment", "title": "Deployment", "icon": "🚀",
             "fields": ["environment", "auto_deploy", "rollback"]},
            {"id": "danger", "title": "Danger Zone", "icon": "⚠️",
             "fields": ["transfer", "archive", "delete"]},
        ],
    }
