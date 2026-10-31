"""Marketplace summary — the definitive platform marketplace summary."""
from __future__ import annotations


def build_marketplace_summary() -> dict:
    return {
        "platform": "OpenSkill Developer Platform",
        "version": "5.0.0",
        "stats": {
            "total_apps": 500, "total_developers": 200,
            "total_installs": 2500000, "total_api_calls_daily": 50000000,
            "avg_rating": 4.3, "total_reviews": 15000,
            "uptime_pct": 99.99, "categories": 8,
        },
        "top_categories": [
            {"name": "Communication", "icon": "💬", "apps": 85},
            {"name": "Developer Tools", "icon": "🛠️", "apps": 72},
            {"name": "Analytics", "icon": "📊", "apps": 65},
            {"name": "Automation", "icon": "⚙️", "apps": 58},
            {"name": "Security", "icon": "🔒", "apps": 45},
        ],
        "highlights": {
            "new_apps_30d": 35, "trending_up": True,
            "developer_satisfaction": 92,
            "avg_install_time_sec": 12,
        },
        "status": "FULLY OPERATIONAL",
    }
