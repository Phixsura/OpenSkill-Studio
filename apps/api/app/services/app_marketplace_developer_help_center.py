"""Developer help center — centralized help with guides, videos, and support."""

HELP_SECTIONS = [
    {"id": "quickstart", "title": "Quick Start Guide", "icon": "🚀", "article_count": 5,
     "description": "Get up and running in 5 minutes"},
    {"id": "sdk", "title": "SDK Documentation", "icon": "📦", "article_count": 12,
     "description": "TypeScript and Python SDK reference"},
    {"id": "webhooks", "title": "Webhooks & Events", "icon": "🔗", "article_count": 8,
     "description": "Set up and manage webhooks"},
    {"id": "marketplace", "title": "Marketplace Guide", "icon": "🏪", "article_count": 10,
     "description": "Publishing and managing apps"},
    {"id": "billing", "title": "Billing & Plans", "icon": "💳", "article_count": 6,
     "description": "Plans, pricing, and payouts"},
    {"id": "security", "title": "Security Best Practices", "icon": "🔒", "article_count": 7,
     "description": "OAuth, HMAC, and secure coding"},
    {"id": "troubleshooting", "title": "Troubleshooting", "icon": "🔧", "article_count": 15,
     "description": "Common issues and solutions"},
]


def build_help_center() -> dict:
    total_articles = sum(s["article_count"] for s in HELP_SECTIONS)
    return {"title": "Help Center", "sections": HELP_SECTIONS,
            "total_articles": total_articles, "search_enabled": True,
            "contact_url": "/support/contact", "community_url": "/community"}


def search_help(*, query: str, articles: list[dict]) -> list[dict]:
    q = query.lower()
    results = []
    for a in articles:
        score = 0
        if q in a.get("title", "").lower():
            score += 10
        if q in a.get("content", "").lower():
            score += 5
        if q in " ".join(a.get("tags", [])).lower():
            score += 8
        if score > 0:
            results.append({**a, "_score": score})
    return sorted(results, key=lambda r: -r["_score"])
