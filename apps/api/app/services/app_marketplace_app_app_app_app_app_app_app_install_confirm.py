"""App install confirmation — verify installation and display next steps."""
from __future__ import annotations
import html


def build_install_confirmation(*, app_name: str, app_icon: str, version: str,
                                  permissions_granted: list[str],
                                  webhook_url: str = "") -> dict:
    return {
        "app_name": html.escape(app_name), "app_icon": app_icon,
        "version": version,
        "permissions": permissions_granted,
        "permission_count": len(permissions_granted),
        "webhook_configured": bool(webhook_url),
        "status": "installed",
        "next_steps": [
            {"label": "Configure settings", "path": f"/apps/{html.escape(app_name)}/settings"},
            {"label": "View documentation", "path": f"/apps/{html.escape(app_name)}/docs"},
            {"label": "Test integration", "path": f"/apps/{html.escape(app_name)}/test"},
        ],
    }
