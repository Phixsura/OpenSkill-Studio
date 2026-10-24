"""App category manager — organize marketplace apps into categories."""
from __future__ import annotations
import html

CATEGORIES = [
    {"id": "analytics", "label": "Analytics", "icon": "📊", "description": "Data insights and reporting"},
    {"id": "automation", "label": "Automation", "icon": "⚙️", "description": "Workflow automation tools"},
    {"id": "communication", "label": "Communication", "icon": "💬", "description": "Chat, email, notifications"},
    {"id": "developer-tools", "label": "Developer Tools", "icon": "🛠️", "description": "IDEs, debuggers, profilers"},
    {"id": "integrations", "label": "Integrations", "icon": "🔗", "description": "Third-party connectors"},
    {"id": "monitoring", "label": "Monitoring", "icon": "📈", "description": "Uptime, alerting, observability"},
    {"id": "security", "label": "Security", "icon": "🔐", "description": "Auth, scanning, compliance"},
    {"id": "productivity", "label": "Productivity", "icon": "🚀", "description": "Team collaboration tools"},
]


def get_categories() -> list[dict]:
    return list(CATEGORIES)


def get_category(cat_id: str) -> dict | None:
    return next((c for c in CATEGORIES if c["id"] == cat_id), None)


def count_apps_by_category(apps: list[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for a in apps:
        cat = a.get("category", "other")
        counts[cat] = counts.get(cat, 0) + 1
    return [{"id": c["id"], "label": c["label"], "icon": c["icon"],
             "count": counts.get(c["id"], 0)} for c in CATEGORIES]
