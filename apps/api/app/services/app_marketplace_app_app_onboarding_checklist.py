"""Onboarding checklist — guided setup task tracker."""

import html


def build_onboarding_checklist(*, tasks: list[dict], user_name: str = "Developer") -> dict:
    items = []
    completed = 0
    for t in tasks:
        done = t.get("completed", False)
        if done:
            completed += 1
        items.append({
            "id": t["id"],
            "title": html.escape(t.get("title", "")),
            "description": html.escape(t.get("description", "")),
            "completed": done,
            "action_url": t.get("action_url"),
            "icon": t.get("icon", "📋"),
            "required": t.get("required", True),
        })
    total = len(items)
    pct = round(completed / total * 100) if total else 0
    return {"tasks": items, "completed": completed, "total": total,
            "progress_pct": pct, "all_done": completed == total,
            "greeting": f"Welcome, {html.escape(user_name)}!"}
