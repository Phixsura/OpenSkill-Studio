"""Email digest — generate periodic summary emails for developers."""

import html
from datetime import datetime


def build_weekly_digest(*, developer_name: str, period: str, stats: dict,
                          highlights: list[str]) -> dict:
    safe_name = html.escape(developer_name)
    sections = []
    if stats.get("new_installs", 0) > 0:
        sections.append({"title": "📥 New Installs", "value": str(stats["new_installs"]),
                          "change": stats.get("install_change_pct", 0)})
    if stats.get("revenue", 0) > 0:
        sections.append({"title": "💰 Revenue", "value": f"${stats['revenue']:,.2f}",
                          "change": stats.get("revenue_change_pct", 0)})
    if stats.get("new_reviews", 0) > 0:
        sections.append({"title": "⭐ New Reviews", "value": str(stats["new_reviews"]),
                          "change": stats.get("review_change_pct", 0)})
    if stats.get("avg_rating"):
        sections.append({"title": "📊 Avg Rating", "value": str(stats["avg_rating"]),
                          "change": 0})
    return {
        "subject": f"Weekly Digest for {safe_name} — {period}",
        "developer_name": safe_name,
        "period": period,
        "sections": sections,
        "highlights": [html.escape(h) for h in highlights],
        "generated_at": datetime.utcnow().isoformat(),
    }
