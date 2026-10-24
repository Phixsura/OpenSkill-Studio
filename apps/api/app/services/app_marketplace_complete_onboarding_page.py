"""Complete onboarding page — master aggregator for new developer setup wizard."""


def build_complete_onboarding_page(*, developer: dict, onboarding_status: dict,
                                      available_templates: list[dict], tips: list[str]) -> dict:
    return {
        "page_type": "developer_onboarding",
        "developer": {"name": developer.get("display_name"), "email": developer.get("email")},
        "progress": onboarding_status,
        "sections": [
            {"key": "welcome", "title": "Welcome to OpenSkill Developer Platform", "icon": "👋"},
            {"key": "checklist", "title": "Setup Checklist", "icon": "✅", "data": onboarding_status},
            {"key": "templates", "title": "Start from a Template", "icon": "📋",
             "data": {"templates": available_templates[:4]}},
            {"key": "resources", "title": "Developer Resources", "icon": "📚",
             "data": {"links": [
                 {"title": "Documentation", "url": "/docs"},
                 {"title": "API Reference", "url": "/docs/api"},
                 {"title": "Community Forum", "url": "/community"},
             ]}},
        ],
        "tips": tips,
    }
