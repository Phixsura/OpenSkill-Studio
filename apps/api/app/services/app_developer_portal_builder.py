"""Developer portal builder — compile all portal page data."""

from app.services.app_developer_dashboard_builder import build_developer_dashboard
from app.services.app_developer_portal_config import get_portal_config


def build_portal_page(*, developer: dict, apps: list[dict], completed_steps: set[str],
                       total_installs: int = 0, total_executions: int = 0) -> dict:
    dashboard = build_developer_dashboard(
        developer=developer, apps=apps, completed_steps=completed_steps,
        total_installs=total_installs, total_executions=total_executions,
    )
    config = get_portal_config()
    
    quick_actions = []
    if config["features"]["app_creation"]:
        quick_actions.append({"label": "Create App", "icon": "➕", "href": "/dashboard/developer/apps/new"})
    if config["features"]["webhook_testing"]:
        quick_actions.append({"label": "Test Webhooks", "icon": "🧪", "href": "/dashboard/developer/webhooks/test"})
    if config["features"]["analytics_dashboard"]:
        quick_actions.append({"label": "Analytics", "icon": "📊", "href": "/dashboard/developer/analytics"})
    quick_actions.append({"label": "Documentation", "icon": "📖", "href": "/dashboard/developer/docs"})
    
    return {
        **dashboard,
        "config": config,
        "quick_actions": quick_actions,
        "portal_version": "1.0",
    }
