"""Getting started wizard — multi-step app creation wizard data."""

WIZARD_STEPS = [
    {"id": "choose_template", "title": "Choose Template", "description": "Pick a starter template or start from scratch"},
    {"id": "basic_info", "title": "Basic Info", "description": "Name, slug, category, description"},
    {"id": "manifest", "title": "Configure Manifest", "description": "Permissions, sandbox, events"},
    {"id": "test", "title": "Test", "description": "Test your app in the sandbox"},
    {"id": "submit", "title": "Submit", "description": "Submit for review and publish"},
]


def get_wizard_steps() -> list[dict]:
    return WIZARD_STEPS


def get_wizard_progress(completed: set[str]) -> dict:
    total = len(WIZARD_STEPS)
    done = sum(1 for s in WIZARD_STEPS if s["id"] in completed)
    current = next((s for s in WIZARD_STEPS if s["id"] not in completed), None)
    return {"total": total, "done": done, "pct": round(done / total * 100), "current_step": current}
