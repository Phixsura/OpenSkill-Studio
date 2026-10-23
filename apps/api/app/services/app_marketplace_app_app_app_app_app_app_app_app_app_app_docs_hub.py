"""Docs hub — comprehensive documentation hub with all sections."""

import html

DOC_SECTIONS = [
    {"id": "quickstart", "title": "Quickstart Guide", "icon": "🚀", "pages": 5, "estimated_min": 10},
    {"id": "concepts", "title": "Core Concepts", "icon": "💡", "pages": 12, "estimated_min": 30},
    {"id": "api", "title": "API Reference", "icon": "📋", "pages": 25, "estimated_min": 0},
    {"id": "sdks", "title": "SDK Documentation", "icon": "📦", "pages": 8, "estimated_min": 20},
    {"id": "webhooks", "title": "Webhooks Guide", "icon": "🔗", "pages": 6, "estimated_min": 15},
    {"id": "security", "title": "Security Best Practices", "icon": "🔒", "pages": 10, "estimated_min": 25},
    {"id": "deployment", "title": "Deployment Guide", "icon": "🚀", "pages": 8, "estimated_min": 20},
    {"id": "troubleshooting", "title": "Troubleshooting", "icon": "🔧", "pages": 15, "estimated_min": 0},
    {"id": "changelog", "title": "API Changelog", "icon": "📝", "pages": 20, "estimated_min": 0},
    {"id": "migration", "title": "Migration Guides", "icon": "🔄", "pages": 5, "estimated_min": 15},
]


def build_docs_hub(*, search_query: str = "") -> dict:
    sections = DOC_SECTIONS
    if search_query:
        q = search_query.lower()
        sections = [s for s in sections if q in s["title"].lower()]
    total_pages = sum(s["pages"] for s in sections)
    total_min = sum(s["estimated_min"] for s in sections)
    return {
        "sections": [{"id": s["id"], "title": s["title"], "icon": s["icon"],
                       "pages": s["pages"], "estimated_min": s["estimated_min"]}
                      for s in sections],
        "total_sections": len(sections), "total_pages": total_pages,
        "total_reading_min": total_min,
        "search_query": search_query,
    }
