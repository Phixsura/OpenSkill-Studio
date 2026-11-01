"""Developer community forum — topics, replies, and engagement."""
from __future__ import annotations
import html


def create_topic(*, title: str, body: str, author: str,
                   category: str = "general", tags: list[str] | None = None) -> dict:
    return {
        "title": html.escape(title), "body": html.escape(body[:5000]),
        "author": author, "category": category, "tags": tags or [],
        "replies": 0, "views": 0, "likes": 0, "pinned": False, "solved": False,
    }


def build_forum_page(topics: list[dict], *, sort: str = "recent") -> dict:
    if sort == "popular":
        topics = sorted(topics, key=lambda t: -(t.get("views", 0) + t.get("likes", 0) * 3))
    elif sort == "unanswered":
        topics = [t for t in topics if t.get("replies", 0) == 0]
    total = len(topics)
    by_category: dict[str, int] = {}
    for t in topics:
        cat = t.get("category", "general")
        by_category[cat] = by_category.get(cat, 0) + 1
    return {"topics": topics, "total": total, "sort": sort,
            "by_category": by_category}
