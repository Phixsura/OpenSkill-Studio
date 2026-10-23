"""Platform tour guide — interactive product tour with step targeting."""
from __future__ import annotations


TOURS = {
    "getting_started": [
        {"id": "welcome", "title": "Welcome to OpenSkill!", "body": "Let's get you set up.", "target": "#dashboard", "position": "bottom"},
        {"id": "create_app", "title": "Create Your First App", "body": "Click here to register your application.", "target": "#create-app-btn", "position": "right"},
        {"id": "api_key", "title": "Generate API Key", "body": "You'll need this to authenticate.", "target": "#api-keys", "position": "bottom"},
        {"id": "docs", "title": "Read the Docs", "body": "Full API reference and guides.", "target": "#docs-link", "position": "left"},
        {"id": "done", "title": "You're All Set! 🎉", "body": "Start building amazing integrations.", "target": "", "position": "center"},
    ],
    "marketplace": [
        {"id": "browse", "title": "Browse Apps", "body": "Discover integrations.", "target": "#marketplace", "position": "bottom"},
        {"id": "install", "title": "Install an App", "body": "One click to add.", "target": "#install-btn", "position": "right"},
    ],
}


def get_tour(tour_id: str) -> dict:
    steps = TOURS.get(tour_id)
    if not steps:
        return {"error": f"Tour '{tour_id}' not found"}
    return {"tour_id": tour_id, "steps": steps, "total_steps": len(steps)}


def track_progress(tour_id: str, completed_steps: list[str]) -> dict:
    steps = TOURS.get(tour_id, [])
    total = len(steps)
    done = len(completed_steps)
    pct = round(done / max(total, 1) * 100)
    next_step = None
    for s in steps:
        if s["id"] not in completed_steps:
            next_step = s["id"]
            break
    return {"tour_id": tour_id, "completed": done, "total": total,
            "progress_pct": pct, "next_step": next_step,
            "finished": done >= total}


def list_tours() -> list[dict]:
    return [{"tour_id": k, "steps": len(v)} for k, v in TOURS.items()]
