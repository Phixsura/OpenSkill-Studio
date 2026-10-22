"""Developer onboarding — track and guide new developer setup progress."""

ONBOARDING_STEPS = [
    {"key": "create_account", "label": "Create Developer Account", "required": True},
    {"key": "create_app", "label": "Create Your First App", "required": True},
    {"key": "add_manifest", "label": "Configure App Manifest", "required": True},
    {"key": "create_version", "label": "Create First Version", "required": True},
    {"key": "submit_review", "label": "Submit for Review", "required": True},
    {"key": "add_webhook", "label": "Configure Webhook URL", "required": False},
    {"key": "add_secrets", "label": "Add App Secrets", "required": False},
    {"key": "generate_api_key", "label": "Generate API Key", "required": False},
]


def get_onboarding_progress(completed_steps: set[str]) -> dict:
    """Calculate onboarding progress."""
    total = len(ONBOARDING_STEPS)
    done = sum(1 for s in ONBOARDING_STEPS if s["key"] in completed_steps)
    required_total = sum(1 for s in ONBOARDING_STEPS if s["required"])
    required_done = sum(1 for s in ONBOARDING_STEPS if s["required"] and s["key"] in completed_steps)

    return {
        "total_steps": total,
        "completed_steps": done,
        "progress_pct": round(done / total * 100) if total > 0 else 0,
        "required_complete": required_done >= required_total,
        "next_step": next((s for s in ONBOARDING_STEPS if s["key"] not in completed_steps), None),
        "steps": [{**s, "completed": s["key"] in completed_steps} for s in ONBOARDING_STEPS],
    }
