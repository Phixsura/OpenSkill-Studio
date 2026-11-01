"""App onboarding progress — track app setup completion."""

import html

SETUP_STEPS = [
    {"id": "basic_info", "title": "Basic Info", "description": "Name, icon, description", "required": True},
    {"id": "permissions", "title": "Permissions", "description": "Define required permissions", "required": True},
    {"id": "webhook_url", "title": "Webhook URL", "description": "Configure event endpoint", "required": False},
    {"id": "screenshots", "title": "Screenshots", "description": "Upload at least 2 screenshots", "required": True},
    {"id": "privacy_policy", "title": "Privacy Policy", "description": "Add privacy policy URL", "required": True},
    {"id": "test_install", "title": "Test Install", "description": "Verify installation flow", "required": True},
]


def build_setup_progress(*, completed: list[str]) -> dict:
    done = set(completed)
    steps = []
    for s in SETUP_STEPS:
        steps.append({**s, "completed": s["id"] in done, "title": html.escape(s["title"])})
    required_done = all(s["completed"] for s in steps if s["required"])
    total_done = sum(1 for s in steps if s["completed"])
    pct = round(total_done / len(steps) * 100)
    next_step = next((s for s in steps if not s["completed"] and s["required"]),
                      next((s for s in steps if not s["completed"]), None))
    return {"steps": steps, "total": len(steps), "completed": total_done,
            "progress_pct": pct, "ready_to_publish": required_done,
            "next_step": next_step}
