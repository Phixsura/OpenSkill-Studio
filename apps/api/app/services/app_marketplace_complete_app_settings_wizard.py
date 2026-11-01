"""Complete app settings wizard — step-by-step configuration flow."""


def build_settings_wizard(*, app: dict, current_step: int = 0) -> dict:
    steps = [
        {"step": 0, "key": "basic_info", "title": "Basic Information", "fields": ["name", "description", "category"]},
        {"step": 1, "key": "permissions", "title": "Permissions & Scopes", "fields": ["required_scopes", "optional_scopes"]},
        {"step": 2, "key": "webhooks", "title": "Webhook Configuration", "fields": ["webhook_url", "events"]},
        {"step": 3, "key": "ui_extensions", "title": "UI Extensions", "fields": ["surfaces", "entry_points"]},
        {"step": 4, "key": "review", "title": "Review & Submit", "fields": []},
    ]
    for s in steps:
        s["status"] = "completed" if s["step"] < current_step else "current" if s["step"] == current_step else "pending"
    return {
        "app_id": app.get("id"), "steps": steps, "current_step": current_step,
        "total_steps": len(steps), "progress_pct": round(current_step / len(steps) * 100),
        "can_submit": current_step >= len(steps) - 1,
    }
