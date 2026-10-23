"""App wizard v3 — comprehensive app creation wizard with live preview."""

WIZARD_STEPS = [
    {"key": "basics", "title": "App Basics", "fields": ["name", "slug", "category", "description"], "required": True},
    {"key": "manifest", "title": "App Manifest", "fields": ["entry_point", "permissions", "events"], "required": True},
    {"key": "branding", "title": "Branding", "fields": ["icon", "screenshots", "color_scheme"], "required": False},
    {"key": "config", "title": "Configuration Schema", "fields": ["config_fields", "defaults"], "required": False},
    {"key": "webhooks", "title": "Webhook Setup", "fields": ["webhook_url", "events", "secret"], "required": False},
    {"key": "review", "title": "Review & Submit", "fields": [], "required": True},
]


def get_wizard_steps() -> list[dict]:
    return WIZARD_STEPS


def compute_wizard_progress(*, completed_steps: list[str]) -> dict:
    total = len(WIZARD_STEPS)
    completed = sum(1 for s in WIZARD_STEPS if s["key"] in completed_steps)
    required_done = all(s["key"] in completed_steps for s in WIZARD_STEPS if s["required"])
    return {"completed": completed, "total": total, "pct": round(completed / total * 100),
            "required_complete": required_done, "can_submit": required_done,
            "next_step": next((s["key"] for s in WIZARD_STEPS if s["key"] not in completed_steps), None)}


def validate_wizard_step(*, step_key: str, data: dict) -> dict:
    errors = []
    if step_key == "basics":
        if not data.get("name") or len(data["name"]) < 3:
            errors.append("App name is required (min 3 chars)")
        if not data.get("slug"):
            errors.append("Slug is required")
        if not data.get("category"):
            errors.append("Category is required")
    elif step_key == "manifest":
        if not data.get("entry_point"):
            errors.append("Entry point is required")
        if not data.get("permissions"):
            errors.append("At least one permission is required")
    return {"valid": len(errors) == 0, "errors": errors, "step": step_key}
