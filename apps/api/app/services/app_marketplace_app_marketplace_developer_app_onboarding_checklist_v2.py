"""Onboarding checklist v2 — gamified checklist with rewards."""

CHECKLIST_ITEMS = [
    {"id": "create_account", "title": "Create developer account", "points": 10, "category": "setup"},
    {"id": "complete_profile", "title": "Complete your profile", "points": 15, "category": "setup"},
    {"id": "read_docs", "title": "Read the documentation", "points": 5, "category": "learn"},
    {"id": "create_app", "title": "Create your first app", "points": 25, "category": "build"},
    {"id": "add_manifest", "title": "Add app manifest", "points": 15, "category": "build"},
    {"id": "run_tests", "title": "Run tests in sandbox", "points": 20, "category": "build"},
    {"id": "submit_review", "title": "Submit for review", "points": 25, "category": "publish"},
    {"id": "get_published", "title": "Get app published", "points": 30, "category": "publish"},
    {"id": "first_install", "title": "Get first installation", "points": 20, "category": "grow"},
    {"id": "first_review", "title": "Receive first review", "points": 15, "category": "grow"},
]


def get_checklist_progress(*, completed: list[str]) -> dict:
    total_points = sum(i["points"] for i in CHECKLIST_ITEMS)
    earned = sum(i["points"] for i in CHECKLIST_ITEMS if i["id"] in completed)
    items = [{**i, "completed": i["id"] in completed} for i in CHECKLIST_ITEMS]
    next_item = next((i for i in items if not i["completed"]), None)
    return {"items": items, "completed_count": len(completed), "total_count": len(CHECKLIST_ITEMS),
            "points_earned": earned, "points_total": total_points,
            "pct": round(earned / total_points * 100), "next_item": next_item}
