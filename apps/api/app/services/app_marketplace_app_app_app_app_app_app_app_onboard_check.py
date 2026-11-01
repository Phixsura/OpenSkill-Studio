"""Platform onboarding checklist — track new team member onboarding."""
from __future__ import annotations
import time


CHECKLIST = [
    {"id": "account", "title": "Create account", "category": "setup", "required": True},
    {"id": "mfa", "title": "Enable MFA", "category": "security", "required": True},
    {"id": "ssh_key", "title": "Add SSH key", "category": "security", "required": True},
    {"id": "team_join", "title": "Join team", "category": "setup", "required": True},
    {"id": "repo_access", "title": "Get repo access", "category": "development", "required": True},
    {"id": "local_env", "title": "Set up local env", "category": "development", "required": True},
    {"id": "first_pr", "title": "Submit first PR", "category": "development", "required": False},
    {"id": "docs_read", "title": "Read documentation", "category": "learning", "required": False},
]


def get_checklist(completed: list[str]) -> dict:
    items = []
    for item in CHECKLIST:
        done = item["id"] in completed
        items.append({**item, "completed": done})
    total = len(CHECKLIST)
    done_count = sum(1 for i in items if i["completed"])
    required_done = all(i["completed"] for i in items if i["required"])
    return {"items": items, "total": total, "completed": done_count,
            "progress_pct": round(done_count / total * 100),
            "required_complete": required_done,
            "ready_to_contribute": required_done}
