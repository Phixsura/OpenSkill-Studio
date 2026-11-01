"""App welcome screen — post-install welcome experience."""

import html


def build_welcome_screen(*, app_name: str, app_icon: str = "📦",
                            features: list[dict] | None = None,
                            next_steps: list[dict] | None = None) -> dict:
    default_features = [
        {"title": "Easy Setup", "description": "Get started in minutes", "icon": "⚡"},
        {"title": "Real-time Updates", "description": "Stay in sync automatically", "icon": "🔄"},
        {"title": "Secure by Default", "description": "Enterprise-grade security", "icon": "🔒"},
    ]
    default_steps = [
        {"title": "Configure Settings", "href": "/settings", "icon": "⚙️"},
        {"title": "View Documentation", "href": "/docs", "icon": "📖"},
        {"title": "Join Community", "href": "/community", "icon": "💬"},
    ]
    return {
        "app_name": html.escape(app_name),
        "app_icon": app_icon,
        "headline": f"Welcome to {html.escape(app_name)}! 🎉",
        "features": features or default_features,
        "next_steps": next_steps or default_steps,
        "dismissible": True,
    }
