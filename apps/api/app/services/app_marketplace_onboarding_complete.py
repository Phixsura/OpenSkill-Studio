"""Onboarding complete — celebration page when developer finishes setup."""


def build_onboarding_complete(*, developer: dict, first_app: dict | None,
                                   stats: dict) -> dict:
    achievements = ["Created developer account", "Completed profile"]
    if first_app:
        achievements.append(f"Created {first_app['name']}")
        if first_app.get("status") == "published":
            achievements.append("Published to marketplace!")
    next_steps = [
        {"label": "View your dashboard", "url": "/developer", "icon": "📊"},
        {"label": "Explore the marketplace", "url": "/marketplace", "icon": "🏪"},
        {"label": "Read the documentation", "url": "/docs", "icon": "📚"},
        {"label": "Join the community", "url": "/community", "icon": "💬"},
    ]
    return {
        "page_type": "onboarding_complete",
        "message": f"Welcome to OpenSkill, {developer.get('display_name', 'Developer')}!",
        "achievements": achievements,
        "next_steps": next_steps,
        "show_confetti": True,
    }
