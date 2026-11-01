"""Developer portal — aggregate developer resources and quickstarts."""
from __future__ import annotations


QUICKSTARTS = [
    {"id": "sdk-setup", "title": "SDK Quick Start", "time_min": 5, "category": "getting-started"},
    {"id": "first-app", "title": "Build Your First App", "time_min": 15, "category": "getting-started"},
    {"id": "webhooks", "title": "Set Up Webhooks", "time_min": 10, "category": "integration"},
    {"id": "auth", "title": "OAuth Integration", "time_min": 20, "category": "security"},
    {"id": "deploy", "title": "Deploy to Production", "time_min": 10, "category": "deployment"},
    {"id": "monitoring", "title": "Add Monitoring", "time_min": 15, "category": "observability"},
]


def get_portal(completed: list[str]) -> dict:
    items = []
    for qs in QUICKSTARTS:
        items.append({**qs, "completed": qs["id"] in completed})
    done = sum(1 for i in items if i["completed"])
    total_time = sum(qs["time_min"] for qs in QUICKSTARTS)
    remaining_time = sum(qs["time_min"] for qs in QUICKSTARTS if qs["id"] not in completed)
    return {"quickstarts": items, "total": len(items), "completed": done,
            "progress_pct": round(done / len(items) * 100),
            "total_time_min": total_time, "remaining_time_min": remaining_time}


def portal_stats(developers: int, apps_published: int, api_calls_today: int) -> dict:
    return {"developers": developers, "apps_published": apps_published,
            "api_calls_today": api_calls_today,
            "display_calls": f"{api_calls_today / 1_000_000:.1f}M" if api_calls_today >= 1_000_000 else f"{api_calls_today:,}"}
