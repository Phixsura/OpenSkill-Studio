"""Complete onboarding flow — the entire new developer onboarding experience."""

ONBOARDING_STEPS = [
    {"key": "welcome", "title": "Welcome", "type": "info", "required": True,
     "content": "Welcome to the OpenSkill Developer Platform! Let's get you set up."},
    {"key": "profile", "title": "Create Profile", "type": "form", "required": True,
     "fields": ["display_name", "slug", "bio", "support_email"]},
    {"key": "first_app", "title": "Create Your First App", "type": "wizard", "required": True,
     "fields": ["app_name", "category", "description"]},
    {"key": "manifest", "title": "Upload Manifest", "type": "upload", "required": True,
     "accepted_formats": ["json", "yaml"]},
    {"key": "test", "title": "Test in Sandbox", "type": "action", "required": False,
     "description": "Test your app in our sandbox environment before publishing"},
    {"key": "submit", "title": "Submit for Review", "type": "action", "required": True,
     "description": "Our team will review your app within 2-3 business days"},
]


def build_onboarding_flow(*, completed_steps: list[str], developer: dict | None = None) -> dict:
    steps = []
    for s in ONBOARDING_STEPS:
        steps.append({**s, "completed": s["key"] in completed_steps,
                        "current": s["key"] not in completed_steps and all(
                            prev["key"] in completed_steps for prev in ONBOARDING_STEPS[:ONBOARDING_STEPS.index(s)])})
    completed = sum(1 for s in steps if s["completed"])
    total = len(steps)
    required_done = all(s["key"] in completed_steps for s in ONBOARDING_STEPS if s["required"])
    return {
        "page_type": "onboarding_flow",
        "steps": steps, "completed": completed, "total": total,
        "progress_pct": round(completed / total * 100),
        "required_complete": required_done,
        "current_step": next((s for s in steps if s.get("current")), None),
        "can_skip_to_publish": required_done,
        "estimated_time_minutes": (total - completed) * 5,
    }


def get_onboarding_tips(*, current_step: str) -> list[str]:
    tips = {
        "welcome": ["Take a quick tour of the platform", "Check out example apps for inspiration"],
        "profile": ["Use a company name if building for a team", "Add a professional bio to build trust"],
        "first_app": ["Choose a descriptive name", "Pick the right category for discoverability"],
        "manifest": ["Use our manifest validator before uploading", "Include all required permissions"],
        "test": ["Test webhook deliveries", "Verify OAuth flow works end-to-end"],
        "submit": ["Write clear release notes", "Include screenshots for faster review"],
    }
    return tips.get(current_step, ["You're making great progress!"])
