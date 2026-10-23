"""Marketplace category grid — browse all marketplace categories."""

import html

MARKETPLACE_CATEGORIES = [
    {"id": "tools", "name": "Developer Tools", "icon": "🔧", "description": "Build faster", "count": 320},
    {"id": "productivity", "name": "Productivity", "icon": "⚡", "description": "Work smarter", "count": 280},
    {"id": "communication", "name": "Communication", "icon": "💬", "description": "Stay connected", "count": 150},
    {"id": "analytics", "name": "Analytics", "icon": "📊", "description": "Data insights", "count": 120},
    {"id": "security", "name": "Security", "icon": "🔒", "description": "Stay protected", "count": 95},
    {"id": "integration", "name": "Integrations", "icon": "🔗", "description": "Connect everything", "count": 250},
    {"id": "automation", "name": "Automation", "icon": "🤖", "description": "Automate workflows", "count": 180},
    {"id": "monitoring", "name": "Monitoring", "icon": "📡", "description": "Watch everything", "count": 110},
    {"id": "testing", "name": "Testing", "icon": "🧪", "description": "Quality assurance", "count": 85},
    {"id": "design", "name": "Design", "icon": "🎨", "description": "Create beautiful UI", "count": 70},
    {"id": "data", "name": "Data & Storage", "icon": "🗃️", "description": "Manage data", "count": 90},
    {"id": "ai", "name": "AI & ML", "icon": "🤖", "description": "Intelligent apps", "count": 130},
]


def build_category_grid() -> dict:
    items = [{"id": c["id"], "name": html.escape(c["name"]), "icon": c["icon"],
              "description": html.escape(c["description"]), "count": c["count"]}
             for c in MARKETPLACE_CATEGORIES]
    total_apps = sum(c["count"] for c in items)
    return {"categories": items, "total": len(items), "total_apps": total_apps}
