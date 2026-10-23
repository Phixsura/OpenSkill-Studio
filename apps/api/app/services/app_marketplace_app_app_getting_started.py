"""Getting started — complete onboarding guide for new developers."""


def build_getting_started(*, developer_name: str, completed: list[str]) -> dict:
    steps = [
        {"id": "signup", "title": "Create Account", "icon": "👤", "time_min": 2},
        {"id": "verify", "title": "Verify Email", "icon": "📧", "time_min": 1},
        {"id": "profile", "title": "Set Up Profile", "icon": "🎨", "time_min": 3},
        {"id": "create_app", "title": "Create First App", "icon": "📦", "time_min": 5},
        {"id": "add_sdk", "title": "Install SDK", "icon": "🔧", "time_min": 5},
        {"id": "first_api", "title": "Make First API Call", "icon": "⚡", "time_min": 3},
        {"id": "deploy", "title": "Deploy to Production", "icon": "🚀", "time_min": 10},
        {"id": "publish", "title": "Publish to Marketplace", "icon": "🏪", "time_min": 5},
    ]
    enriched = [{"completed": s["id"] in completed, **s} for s in steps]
    done = sum(1 for s in enriched if s["completed"])
    current = next((s for s in enriched if not s["completed"]), None)
    total_time = sum(s["time_min"] for s in enriched if not s["completed"])
    return {
        "developer_name": developer_name,
        "steps": enriched,
        "completed": done,
        "total": len(enriched),
        "pct": round(done / len(enriched) * 100),
        "current_step": current,
        "remaining_time_min": total_time,
        "all_done": done == len(enriched),
    }
