"""Developer blog builder — build blog listing and article pages."""
from __future__ import annotations
import html


def build_blog_listing(posts: list[dict], *, limit: int = 10) -> dict:
    items = []
    for p in posts[:limit]:
        items.append({
            "slug": p.get("slug", ""),
            "title": html.escape(p.get("title", "")),
            "excerpt": html.escape(p.get("excerpt", "")[:200]),
            "author": p.get("author", ""),
            "date": p.get("date", ""),
            "tags": p.get("tags", []),
            "read_time": p.get("read_time", "3 min"),
            "featured": p.get("featured", False),
        })
    featured = [i for i in items if i["featured"]]
    return {"posts": items, "total": len(posts), "shown": len(items),
            "featured": featured}


def get_related_posts(current_tags: list[str], all_posts: list[dict], *, limit: int = 3) -> list[dict]:
    scored = []
    for p in all_posts:
        overlap = len(set(current_tags) & set(p.get("tags", [])))
        if overlap > 0:
            scored.append((overlap, p))
    scored.sort(key=lambda x: -x[0])
    return [{"slug": p.get("slug"), "title": p.get("title"), "date": p.get("date")}
            for _, p in scored[:limit]]
