"""Notification digest builder — aggregate notifications into periodic digests."""
from __future__ import annotations
import html


def build_digest(notifications: list[dict], *, period: str = "daily") -> dict:
    by_category: dict[str, list[dict]] = {}
    for n in notifications:
        cat = n.get("category", "general")
        by_category.setdefault(cat, []).append({
            "title": html.escape(n.get("title", "")),
            "body": html.escape(n.get("body", "")[:200]),
            "priority": n.get("priority", "normal"),
            "timestamp": n.get("timestamp", ""),
        })
    high_priority = sum(1 for n in notifications if n.get("priority") == "high")
    sections = [{"category": cat, "count": len(items), "items": items}
                for cat, items in sorted(by_category.items())]
    return {
        "period": period, "total": len(notifications),
        "high_priority": high_priority, "categories": len(by_category),
        "sections": sections,
        "summary": f"{len(notifications)} notifications ({high_priority} high priority)",
    }
