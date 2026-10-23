"""Developer onboarding — step-by-step developer setup wizard."""

import html

ONBOARDING_STEPS = [
    {"id": "profile", "title": "Complete Profile", "description": "Add your name, bio, and avatar", "icon": "👤", "required": True},
    {"id": "verify_email", "title": "Verify Email", "description": "Confirm your email address", "icon": "📧", "required": True},
    {"id": "create_org", "title": "Create Organization", "description": "Set up your developer organization", "icon": "🏢", "required": False},
    {"id": "install_cli", "title": "Install CLI", "description": "Install the OpenSkill CLI tool", "icon": "💻", "required": True},
    {"id": "first_app", "title": "Create First App", "description": "Build and deploy your first app", "icon": "🚀", "required": False},
    {"id": "connect_github", "title": "Connect GitHub", "description": "Link your GitHub account", "icon": "🐙", "required": False},
]


def build_onboarding(*, completed: list[str]) -> dict:
    done = set(completed)
    steps = []
    for s in ONBOARDING_STEPS:
        steps.append({**s, "completed": s["id"] in done, "title": html.escape(s["title"])})
    required_done = all(s["completed"] for s in steps if s["required"])
    total_done = sum(1 for s in steps if s["completed"])
    pct = round(total_done / len(steps) * 100)
    next_step = next((s for s in steps if not s["completed"]), None)
    return {"steps": steps, "total": len(steps), "completed": total_done,
            "progress_pct": pct, "required_complete": required_done,
            "can_skip_to_dashboard": required_done,
            "next_step": next_step}
