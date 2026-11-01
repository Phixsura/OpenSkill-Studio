"""Developer guide — comprehensive developer documentation index."""

import html

GUIDE_SECTIONS = [
    {"id": "quickstart", "title": "Quickstart", "icon": "🚀", "estimated_min": 5,
     "topics": ["Installation", "Authentication", "First API Call"]},
    {"id": "concepts", "title": "Core Concepts", "icon": "💡", "estimated_min": 15,
     "topics": ["Apps", "Webhooks", "Events", "Permissions", "Sandboxing"]},
    {"id": "guides", "title": "How-to Guides", "icon": "📖", "estimated_min": 30,
     "topics": ["Build an App", "Add OAuth", "Handle Webhooks", "Deploy to Production"]},
    {"id": "api", "title": "API Reference", "icon": "📋", "estimated_min": 0,
     "topics": ["REST API", "Authentication", "Rate Limits", "Error Codes"]},
    {"id": "sdks", "title": "SDKs & Libraries", "icon": "📦", "estimated_min": 10,
     "topics": ["TypeScript SDK", "Python SDK", "Go SDK", "CLI Tool"]},
    {"id": "best_practices", "title": "Best Practices", "icon": "✅", "estimated_min": 20,
     "topics": ["Security", "Performance", "Error Handling", "Testing"]},
]


def build_developer_guide(*, completed_sections: list[str] | None = None) -> dict:
    done = set(completed_sections or [])
    sections = []
    total_min = 0
    for s in GUIDE_SECTIONS:
        total_min += s["estimated_min"]
        sections.append({**s, "completed": s["id"] in done,
                          "topic_count": len(s["topics"])})
    completed = sum(1 for s in sections if s["completed"])
    pct = round(completed / len(sections) * 100)
    return {"sections": sections, "total": len(sections), "completed": completed,
            "progress_pct": pct, "total_reading_min": total_min,
            "next_section": next((s for s in sections if not s["completed"]), None)}
