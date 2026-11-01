"""Onboarding wizard — guided app creation flow."""


WIZARD_STEPS = [
    {"id": "name", "title": "Name Your App", "description": "Choose a unique name", "required": True},
    {"id": "description", "title": "Describe It", "description": "What does your app do?", "required": True},
    {"id": "category", "title": "Pick Category", "description": "Help users find your app", "required": True},
    {"id": "icon", "title": "Upload Icon", "description": "512x512 PNG or SVG", "required": True},
    {"id": "screenshots", "title": "Add Screenshots", "description": "Show your app in action", "required": False},
    {"id": "pricing", "title": "Set Pricing", "description": "Free or paid", "required": True},
    {"id": "review", "title": "Review & Submit", "description": "Final check before publishing", "required": True},
]


def get_wizard_state(*, completed_steps: list[str]) -> dict:
    steps = []
    for step in WIZARD_STEPS:
        done = step["id"] in completed_steps
        steps.append({**step, "completed": done})
    completed_count = sum(1 for s in steps if s["completed"])
    required_done = all(s["completed"] for s in steps if s["required"])
    current = next((s["id"] for s in steps if not s["completed"]), None)
    return {
        "steps": steps,
        "total_steps": len(steps),
        "completed": completed_count,
        "progress_pct": round(completed_count / len(steps) * 100),
        "current_step": current,
        "can_submit": required_done,
    }
