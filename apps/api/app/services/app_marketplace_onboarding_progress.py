"""Onboarding progress — detailed step-by-step onboarding tracking with milestones."""

MILESTONES = [
    {"id": "account", "title": "Create Account", "points": 10, "order": 0},
    {"id": "profile", "title": "Complete Profile", "points": 15, "order": 1},
    {"id": "first_app", "title": "Create First App", "points": 25, "order": 2},
    {"id": "manifest", "title": "Upload Manifest", "points": 20, "order": 3},
    {"id": "first_test", "title": "Run First Test", "points": 15, "order": 4},
    {"id": "submit_review", "title": "Submit for Review", "points": 20, "order": 5},
    {"id": "first_install", "title": "Get First Install", "points": 30, "order": 6},
    {"id": "first_review", "title": "Receive First Review", "points": 15, "order": 7},
]


def get_onboarding_progress(*, completed: list[str]) -> dict:
    total_points = sum(m["points"] for m in MILESTONES)
    earned = sum(m["points"] for m in MILESTONES if m["id"] in completed)
    steps = []
    for m in sorted(MILESTONES, key=lambda x: x["order"]):
        steps.append({**m, "completed": m["id"] in completed})
    next_step = next((s for s in steps if not s["completed"]), None)
    return {"steps": steps, "completed_count": len(completed), "total_count": len(MILESTONES),
            "points_earned": earned, "points_total": total_points,
            "progress_pct": round(earned / total_points * 100),
            "next_step": next_step, "all_complete": len(completed) >= len(MILESTONES)}


def unlock_achievement(*, milestone_id: str) -> dict | None:
    milestone = next((m for m in MILESTONES if m["id"] == milestone_id), None)
    if not milestone:
        return None
    return {"milestone": milestone["title"], "points": milestone["points"],
            "message": f"🎉 Achievement unlocked: {milestone['title']}!"}
