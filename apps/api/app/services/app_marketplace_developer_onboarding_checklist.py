"""Developer onboarding checklist — track new developer setup progress."""


def build_onboarding_checklist(*, developer: dict) -> dict:
    steps = [
        {"id": "profile", "label": "Complete your profile", "required": True,
         "check": lambda d: bool(d.get("display_name") and d.get("avatar"))},
        {"id": "verify_email", "label": "Verify email address", "required": True,
         "check": lambda d: d.get("email_verified", False)},
        {"id": "accept_tos", "label": "Accept Terms of Service", "required": True,
         "check": lambda d: d.get("tos_accepted", False)},
        {"id": "create_app", "label": "Create your first app", "required": False,
         "check": lambda d: d.get("app_count", 0) > 0},
        {"id": "setup_webhook", "label": "Set up a webhook", "required": False,
         "check": lambda d: d.get("webhook_count", 0) > 0},
        {"id": "api_key", "label": "Generate an API key", "required": False,
         "check": lambda d: d.get("has_api_key", False)},
    ]
    results = []
    for s in steps:
        completed = s["check"](developer)
        results.append({"id": s["id"], "label": s["label"],
                         "required": s["required"], "completed": completed})
    done = sum(1 for r in results if r["completed"])
    required_done = all(r["completed"] for r in results if r["required"])
    return {
        "steps": results,
        "completed": done,
        "total": len(results),
        "progress_pct": round(done / len(results) * 100),
        "onboarding_complete": required_done,
    }
