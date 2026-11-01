"""App publish wizard — guide developers through the publishing process."""
from __future__ import annotations
import html

PUBLISH_STEPS = [
    {"id": "listing", "title": "Complete Listing", "description": "Name, description, screenshots"},
    {"id": "security", "title": "Security Review", "description": "Pass automated security scan"},
    {"id": "testing", "title": "Testing", "description": "Install and test in sandbox"},
    {"id": "legal", "title": "Legal", "description": "Accept developer agreements"},
    {"id": "submit", "title": "Submit", "description": "Submit for review"},
]


def build_publish_wizard(completed_steps: list[str]) -> dict:
    steps = []
    for s in PUBLISH_STEPS:
        done = s["id"] in completed_steps
        steps.append({**s, "completed": done})
    current = next((s["id"] for s in steps if not s["completed"]), None)
    done_count = sum(1 for s in steps if s["completed"])
    pct = round(done_count / len(steps) * 100)
    return {"steps": steps, "current_step": current, "completed": done_count,
            "total": len(steps), "progress_pct": pct,
            "ready_to_submit": done_count == len(steps) - 1 and current == "submit",
            "published": done_count == len(steps)}
