"""API docs search — documentation search engine."""

import html
import re
from collections import defaultdict


def search_docs(*, query: str, pages: list[dict], limit: int = 10) -> dict:
    q = query.lower().strip()
    if not q:
        return {"results": [], "total": 0, "query": query}
    tokens = q.split()
    scored = []
    for page in pages:
        title = page.get("title", "")
        body = page.get("body", "")
        content = f"{title} {body}".lower()
        score = sum(content.count(t) for t in tokens)
        title_bonus = sum(2 for t in tokens if t in title.lower())
        score += title_bonus
        if score > 0:
            # Build snippet
            first_match = -1
            for t in tokens:
                idx = content.find(t)
                if idx >= 0 and (first_match < 0 or idx < first_match):
                    first_match = idx
            start = max(0, first_match - 40)
            snippet = body[start:start + 120].strip()
            if start > 0:
                snippet = "..." + snippet
            scored.append({"title": html.escape(title), "path": page.get("path", ""),
                           "snippet": html.escape(snippet), "score": score})
    scored.sort(key=lambda x: -x["score"])
    results = scored[:limit]
    return {"results": results, "total": len(scored), "query": query,
            "shown": len(results)}
