"""Onboarding tour — guided product tour for new users."""


TOUR_STEPS = [
    {"id": "welcome", "title": "Welcome to the Platform!", "description": "Let's show you around.",
     "target": "#hero", "position": "bottom"},
    {"id": "search", "title": "Find Apps", "description": "Search and discover apps.",
     "target": "#search-bar", "position": "bottom"},
    {"id": "categories", "title": "Browse Categories", "description": "Explore apps by category.",
     "target": "#categories", "position": "right"},
    {"id": "install", "title": "Install an App", "description": "Click install to add apps.",
     "target": ".install-btn", "position": "left"},
    {"id": "dashboard", "title": "Your Dashboard", "description": "Manage installed apps here.",
     "target": "#dashboard-link", "position": "bottom"},
    {"id": "done", "title": "You're All Set!", "description": "Start exploring the marketplace.",
     "target": None, "position": "center"},
]


def get_tour(*, user_completed_steps: list[str] | None = None) -> dict:
    completed = set(user_completed_steps or [])
    steps = [{"step": i + 1, **s, "completed": s["id"] in completed} for i, s in enumerate(TOUR_STEPS)]
    current = next((s for s in steps if not s["completed"]), None)
    return {
        "steps": steps,
        "total_steps": len(steps),
        "completed_count": len(completed & {s["id"] for s in TOUR_STEPS}),
        "current_step": current,
        "tour_complete": current is None,
    }
