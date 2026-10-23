"""Marketplace search index — build and query search index for apps."""
from __future__ import annotations
import html


def build_index(apps: list[dict]) -> dict:
    index: dict[str, list[str]] = {}
    for app in apps:
        app_id = app.get("id", "")
        tokens = set()
        for field in ("name", "description", "category", "developer"):
            text = app.get(field, "").lower()
            tokens.update(text.split())
        for tag in app.get("tags", []):
            tokens.add(tag.lower())
        for token in tokens:
            index.setdefault(token, []).append(app_id)
    return {"index_size": len(index), "app_count": len(apps),
            "total_tokens": sum(len(v) for v in index.values()),
            "index": index}


def search_index(index: dict[str, list[str]], query: str, *, limit: int = 20) -> list[str]:
    terms = query.lower().split()
    if not terms:
        return []
    # Intersection of results for all terms
    result_sets = [set(index.get(t, [])) for t in terms]
    if not result_sets:
        return []
    matches = result_sets[0]
    for rs in result_sets[1:]:
        matches &= rs
    return list(matches)[:limit]
