"""Developer onboarding — checklist, progress tracking, guided setup."""

ONBOARDING_STEPS = [
    {"key": "profile", "title": "Complete developer profile", "required": True},
    {"key": "agreement", "title": "Accept developer agreement", "required": True},
    {"key": "first_app", "title": "Create your first app", "required": True},
    {"key": "manifest", "title": "Upload app manifest", "required": True},
    {"key": "version", "title": "Submit first version for review", "required": True},
    {"key": "webhook", "title": "Set up a webhook endpoint", "required": False},
    {"key": "docs", "title": "Add app documentation", "required": False},
    {"key": "icon", "title": "Upload app icon", "required": False},
]


def get_onboarding_status(*, completed_steps: list[str]) -> dict:
    steps = []
    for s in ONBOARDING_STEPS:
        steps.append({**s, "completed": s["key"] in completed_steps})
    required = [s for s in steps if s["required"]]
    completed_required = sum(1 for s in required if s["completed"])
    total_completed = sum(1 for s in steps if s["completed"])
    return {
        "steps": steps,
        "progress_pct": round(total_completed / len(steps) * 100),
        "required_complete": completed_required == len(required),
        "can_publish": completed_required == len(required),
        "next_step": next((s["key"] for s in steps if not s["completed"]), None),
    }


def get_onboarding_tips(*, next_step: str | None) -> list[str]:
    tips = {
        "profile": ["Add a logo and description to build trust", "Include your support email"],
        "agreement": ["Review the terms carefully", "Agreement is required to publish apps"],
        "first_app": ["Choose a descriptive name", "Pick the right category for discoverability"],
        "manifest": ["Use the manifest validator to check for errors", "Include all required permissions"],
        "version": ["Write clear release notes", "Test thoroughly before submitting"],
    }
    return tips.get(next_step or "", ["You're all set! Start building great apps."])
