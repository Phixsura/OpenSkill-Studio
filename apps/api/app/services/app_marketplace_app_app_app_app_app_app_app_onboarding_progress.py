"""Onboarding progress — track new user onboarding completion."""
from __future__ import annotations

ONBOARDING_STEPS = [
    {"id": "profile", "title": "Complete Profile", "weight": 1},
    {"id": "first_app", "title": "Create First App", "weight": 2},
    {"id": "api_key", "title": "Generate API Key", "weight": 1},
    {"id": "first_call", "title": "Make First API Call", "weight": 2},
    {"id": "webhook", "title": "Set Up Webhook", "weight": 1},
    {"id": "invite", "title": "Invite Team Member", "weight": 1},
    {"id": "deploy", "title": "First Deploy", "weight": 3},
]


def compute_progress(completed: list[str]) -> dict:
    total_weight = sum(s["weight"] for s in ONBOARDING_STEPS)
    done_weight = sum(s["weight"] for s in ONBOARDING_STEPS if s["id"] in completed)
    pct = round(done_weight / total_weight * 100)
    steps = [{"id": s["id"], "title": s["title"], "completed": s["id"] in completed,
              "weight": s["weight"]} for s in ONBOARDING_STEPS]
    next_step = next((s for s in steps if not s["completed"]), None)
    return {"steps": steps, "completed_count": len(completed),
            "total_steps": len(ONBOARDING_STEPS), "progress_pct": pct,
            "finished": pct >= 100, "next_step": next_step}


def get_congratulations(progress: dict) -> str | None:
    if progress["finished"]:
        return "🎉 Congratulations! You've completed the onboarding!"
    if progress["progress_pct"] >= 75:
        return "🔥 Almost there! Just a few more steps!"
    if progress["progress_pct"] >= 50:
        return "💪 Halfway done! Keep going!"
    return None
