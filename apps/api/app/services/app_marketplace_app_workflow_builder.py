"""Workflow builder — create automation workflows with triggers and actions."""

import secrets


TRIGGER_TYPES = {
    "webhook": "Incoming webhook",
    "schedule": "Scheduled (cron)",
    "event": "Platform event",
    "manual": "Manual trigger",
}

ACTION_TYPES = {
    "http_request": "HTTP Request",
    "send_email": "Send Email",
    "transform": "Transform Data",
    "condition": "If/Else Condition",
    "delay": "Wait/Delay",
    "notify": "Send Notification",
}


def create_workflow(*, name: str, trigger: dict, actions: list[dict]) -> dict:
    if trigger.get("type") not in TRIGGER_TYPES:
        return {"error": f"Invalid trigger. Valid: {', '.join(sorted(TRIGGER_TYPES))}"}
    if not actions:
        return {"error": "At least one action is required"}
    invalid_actions = [a for a in actions if a.get("type") not in ACTION_TYPES]
    if invalid_actions:
        return {"error": f"Invalid action types: {[a.get('type') for a in invalid_actions]}"}
    steps = [{"step": i + 1, "type": a["type"], "label": ACTION_TYPES[a["type"]],
              "config": a.get("config", {})} for i, a in enumerate(actions)]
    return {
        "workflow_id": f"wf_{secrets.token_urlsafe(8)}",
        "name": name,
        "trigger": {"type": trigger["type"], "label": TRIGGER_TYPES[trigger["type"]],
                     "config": trigger.get("config", {})},
        "steps": steps,
        "total_steps": len(steps),
        "status": "draft",
    }
