"""Platform onboarding flow — guided setup wizard with progress tracking."""
from __future__ import annotations


def create_onboarding(*, user_id: str, plan: str = "free") -> dict:
    steps = [
        {"id": "profile", "title": "Complete Profile", "description": "Set your name and avatar"},
        {"id": "create_app", "title": "Create First App", "description": "Register your application"},
        {"id": "api_key", "title": "Generate API Key", "description": "Create credentials"},
        {"id": "first_request", "title": "Make First API Call", "description": "Send a test request"},
        {"id": "webhook", "title": "Set Up Webhook", "description": "Configure event notifications"},
        {"id": "invite_team", "title": "Invite Team Member", "description": "Collaborate with others"},
    ]
    return {"user_id": user_id, "plan": plan, "steps": [
        {**s, "completed": False, "index": i} for i, s in enumerate(steps)
    ], "total": len(steps), "completed": 0, "progress_pct": 0}


def complete_step(onboarding: dict, step_id: str) -> dict:
    for s in onboarding["steps"]:
        if s["id"] == step_id:
            s["completed"] = True
    done = sum(1 for s in onboarding["steps"] if s["completed"])
    onboarding["completed"] = done
    onboarding["progress_pct"] = round(done / onboarding["total"] * 100)
    finished = done == onboarding["total"]
    return {"step": step_id, "completed_count": done, "progress_pct": onboarding["progress_pct"],
            "finished": finished, "next_step": _next(onboarding)}


def _next(onboarding: dict) -> str | None:
    for s in onboarding["steps"]:
        if not s["completed"]:
            return s["id"]
    return None
